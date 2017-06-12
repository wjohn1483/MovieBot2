import tensorflow as tf
from tensorflow.contrib import rnn
import numpy as np
import random
import json
import argparse
import sys

# Config
word2idx = json.load(open("./data/word_table.json", 'r'))
idx2slot = json.load(open("./data/slots_table.json", 'r'))
idx2intent = json.load(open("./data/intent_table.json", 'r'))
slot2idx = dict((k, v) for v, k in idx2slot.items())
intent2idx = dict((k, v) for v, k in idx2intent.items())
model_dir = "./model/"
model_path = model_dir + "model.ckpt"
training_data_path = "./data/training_data.json"
testing_data_path = "./data/testing_data.json"
output_path = "./prediction.json"
nclass_slot = len(slot2idx)
nclass_intent = len(intent2idx)
print(nclass_intent)
vocsize = len(word2idx)
max_sequence_length = 15 # Defined by myself
rnn_dim = 16
learning_rate = 0.001
batch_size = 100
word_dim = 200
nepoch = 30
save_per_epoch = 5

# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--train", type=bool, default=False)
parser.add_argument("--check_overfitting", type=bool, default=False)
parser.add_argument("--keep_training", type=bool, default=False)
args = parser.parse_args()
tf.app.flags.DEFINE_boolean('train', args.train, "If False, load the pretrained model and test")
tf.app.flags.DEFINE_boolean('check_overfitting', args.check_overfitting, "If True, load the pretrained model and use a batch of training data to test")
tf.app.flags.DEFINE_boolean('keep_training', args.keep_training, "If True, load the pretrained model and keep taining")
FLAGS = tf.app.flags.FLAGS
# End of config

# Define model structure
class RNN_model:
    def __init__(self, rnn_dim, max_sequence_length, vocsize, word_dim, nclass_slot, nclass_intent):
        self.rnn_dim = rnn_dim
        self.max_sequence_length = max_sequence_length
        self.vocsize = vocsize
        self.word_dim = word_dim
        self.nclass_slot = nclass_slot
        self.nclass_intent = nclass_intent

    def build_model(self):
        # Define model inputs
        input_sentences = tf.placeholder(tf.float32, [None, self.max_sequence_length, self.vocsize])
        sequence_length = tf.placeholder(tf.int64, [None])
        sentence_slots = tf.placeholder(tf.int64, [None, self.max_sequence_length])
        sentence_intent = tf.placeholder(tf.int64, [None])

        # Transform words in input sentence to self.word_dim
        W_transform = tf.Variable(tf.random_uniform([self.vocsize, self.word_dim], -0.1, 0.1))
        b_transform = tf.Variable(tf.random_uniform([self.word_dim]))
        input_sequence = tf.reshape(input_sentences, [-1, self.vocsize])
        input_sequence = tf.matmul(input_sequence, W_transform) + b_transform
        input_sequence = tf.transpose(tf.reshape(input_sequence, [-1, self.max_sequence_length, self.word_dim]), [1, 0, 2])
        input_sequence = tf.reshape(input_sequence, [-1, self.word_dim])
        input_sequence = tf.split(input_sequence, int(self.max_sequence_length), int(0))

        # RNN
        lstm_cell = rnn.core_rnn_cell.BasicLSTMCell(self.rnn_dim)
        rnn_outputs, state = rnn.static_rnn(lstm_cell, input_sequence, sequence_length = sequence_length, dtype=tf.float32)

        # Output layer of slot
        W_output_slot = tf.Variable(tf.random_uniform([self.rnn_dim, self.nclass_slot], -0.1, 0.1))
        b_output_slot = tf.Variable(tf.random_uniform([self.nclass_slot]))
        rnn_outputs = tf.reshape(tf.stack(rnn_outputs), [-1, self.rnn_dim])
        logit = tf.matmul(rnn_outputs, W_output_slot) + b_output_slot
        logit = tf.reshape(logit, [self.max_sequence_length, -1, self.nclass_slot])
        prediction_slot = tf.transpose(logit, [1, 0, 2])

        # Output layer of intent
        W_output_intent = tf.Variable(tf.random_uniform([2*self.rnn_dim, self.nclass_intent], -0.1, 0.1))
        b_output_intent = tf.Variable(tf.random_uniform([self.nclass_intent]))
        state_concat = tf.concat([state[0], state[1]], axis=1)
        prediction_intent = tf.matmul(state_concat, W_output_intent) + b_output_intent

        # Define loss and optimizer
        # Loss of slot filling
        loss = 0
        groundtruth_slot = tf.transpose(tf.one_hot(sentence_slots, self.nclass_slot), [1, 0, 2])
        for i in range(self.max_sequence_length):
            cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits = logit[i], labels = groundtruth_slot[i])
            loss += tf.reduce_sum(cross_entropy)
        loss = loss/tf.reduce_sum(tf.to_float(sequence_length))
        # Loss of intent prediction
        groundtruth_intent = tf.one_hot(sentence_intent, self.nclass_intent)
        loss += tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits = prediction_intent, labels = groundtruth_intent))
        train_step = tf.train.AdamOptimizer(learning_rate).minimize(loss)

        return input_sentences, sequence_length, sentence_slots, sentence_intent, train_step, loss, prediction_slot, prediction_intent

# Read data
def read_data(filepath):
    sentences = []
    sequence_length = []
    slots = []
    intents = []

    f = json.load(open(filepath, 'r'))
    for item in f:
        # Convert sentence to 1-hot
        line = item["sentence"].rstrip('\n').split()
        temp = np.zeros((max_sequence_length, vocsize))
        for i, word in enumerate(line):
            if (word in word2idx) and (i<max_sequence_length): temp[i][int(word2idx[word])] = 1
            elif (not (word in word2idx)) and (i<max_sequence_length): temp[i][int(word2idx["_UNK"])] = 1
        sentences.append(temp)
        sequence_length.append(len(line))

        # Store slots
        temp = np.zeros((max_sequence_length))
        line = item["slots"].rstrip('\n').split()
        for i, slot in enumerate(line):
            if i < max_sequence_length: temp[i] = int(slot2idx[slot])
        slots.append(temp)

        # Store intents
        intents.append(int(intent2idx[item["intent"]]))

    return sentences, sequence_length, slots, intents

def restore():
    sess = tf.Session()
    input_sentences, sequence_length, sentence_slots, sentence_intent, train_step, loss, prediction_slot, prediction_intent = RNN_model(rnn_dim=rnn_dim, max_sequence_length=max_sequence_length, vocsize=vocsize, word_dim=word_dim, nclass_slot=nclass_slot, nclass_intent=nclass_intent).build_model()
    tf.train.Saver().restore(sess, tf.train.latest_checkpoint(model_dir))

    return sess, input_sentences, sequence_length, prediction_slot, prediction_intent

def slot_filling_and_intent_prediction(input_string, sess, input_sentences, sequence_length, prediction_slot, prediction_intent):
    # Convert sentence to 1-hot
    sentence = []
    length = []
    temp = np.zeros((max_sequence_length, vocsize))
    line = input_string.rstrip('\n').split()
    for i, word in enumerate(line):
        if (word in word2idx) and (i<max_sequence_length): temp[i][int(word2idx[word])] = 1
        elif (not (word in word2idx)) and (i<max_sequence_length): temp[i][int(word2idx["_UNK"])] = 1
    sentence.append(temp)
    length.append(len(line))

    # Make prediction
    feed_dict = {input_sentences: sentence, sequence_length: length}
    predict = sess.run(prediction_slot, feed_dict)

    # Convert to slots
    predict_string = ""
    for i in range(length[0]):
        predict_string += idx2slot[str(np.argmax(predict[0][i]))] + ' '

    return predict_string.rstrip(' '), np.argmax(sess.run(prediction_intent, feed_dict))

if __name__ == "__main__":
    # Create model
    sess = tf.Session()
    input_sentences, sequence_length, sentence_slots, sentence_intent, train_step, loss, prediction_slot, prediction_intent = RNN_model(rnn_dim=rnn_dim, max_sequence_length=max_sequence_length, vocsize=vocsize, word_dim=word_dim, nclass_slot=nclass_slot, nclass_intent=nclass_intent).build_model()

    # Train
    if FLAGS.train:
        if FLAGS.keep_training == False: tf.global_variables_initializer().run(session = sess)
        else:
            tf.train.Saver().restore(sess, tf.train.latest_checkpoint(model_dir))
            print("Succcessfully load model")

        # Read data
        sentences, length, slots, intents = read_data(training_data_path)

        epoch = 0
        while epoch < nepoch:
            # Prepare batch input
            for i in range(0, len(sentences), batch_size):
                sentences_batch = sentences[i:i+batch_size]
                sequence_length_batch = length[i:i+batch_size]
                slots_batch = slots[i:i+batch_size]
                intents_batch = intents[i:i+batch_size]

                # Update parameters
                feed_dict = {input_sentences: sentences_batch, sequence_length: sequence_length_batch, sentence_slots: slots_batch, sentence_intent: intents_batch}
                sess.run(train_step, feed_dict)

            # Print loss
            epoch += 1
            training_loss = sess.run(loss, feed_dict)
            print("End of epoch " + str(epoch) + " : training loss = " + str(training_loss))
            sys.stdout.flush()

            # Shuffle data
            temp = list(zip(sentences, length, slots, intents))
            random.shuffle(temp)
            sentences, length, slots, intents = zip(*temp)

            # Save model
            if epoch % save_per_epoch == 0:
                tf.train.Saver(max_to_keep=10).save(sess, model_path, global_step=epoch)
                print("Model saved in file:" + model_path + "-" + str(epoch))
                sys.stdout.flush()

    # Test
    else:
        tf.train.Saver().restore(sess, tf.train.latest_checkpoint(model_dir))
        print("Successfully load model")

        # Read testing data
        if FLAGS.check_overfitting:
            sentences, length, slots, intents = read_data(training_data_path)
            sentences = sentences[0:batch_size]
            length = length[0:batch_size]
            slots = slots[0:batch_size]
            intents = intents[0:batch_size]
        else:
            sentences, length, slots, intents = read_data(testing_data_path)

        # Predict and output
        feed_dict = {input_sentences: sentences, sequence_length: length, sentence_slots: slots, sentence_intent: intents}
        testing_loss = sess.run(loss, feed_dict)
        predicts_slot = sess.run(prediction_slot, feed_dict)
        predicts_intent = sess.run(prediction_intent, feed_dict)
        print("Testing loss = " + str(testing_loss))

        outputs = []
        for i, predict in enumerate(predicts_slot):
            groundtruth_string = ""
            predict_string = ""
            for j in range(length[i]):
                groundtruth_string += idx2slot[str(int(slots[i][j]))] + ' '
                predict_string += idx2slot[str(np.argmax(predict[j]))] + ' '
            outputs.append({"groundtruth_slot": groundtruth_string, "groundtruth_intent": idx2intent[str(intents[i])], "prediction_slot": predict_string, "prediction_intent": idx2intent[str(np.argmax(predicts_intent[i]))]})

        json.dump(outputs, open(output_path, 'w'), indent=4)
        print("Prediction saved in file: " + str(output_path))
