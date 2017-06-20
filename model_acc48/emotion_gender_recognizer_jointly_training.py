import tensorflow as tf
from tensorflow.contrib import rnn
import numpy as np
import random
import json
import sys

# Config
#training_data = json.load(open("./training_data_mfcc.json", 'r'))
#testing_data = json.load(open("./testing_data_mfcc.json", 'r'))
#feature_dir = "./mfcc_npy/"
emotion_table = json.load(open("./model_acc48/emotion_table.json", 'r'))
feature_dir = "./audio2vec_feat/"
model_dir = "./model_acc48/"
model_path = model_dir + "model.ckpt"
batch_size = 16
rnn_dim = 64
max_sequence_length = 30 # Max sequence length in data is 413
nclass_emotion = 5
input_dim = 300
nepoch = 15
learning_rate = 0.001
dropout_rate = 0.1
# End of configuration

class EmotionGenderRecognizer:
    def __init__(self, rnn_dim, max_sequence_length, input_dim, nclass_emotion):
        self.rnn_dim = rnn_dim
        self.max_sequence_length = max_sequence_length
        self.input_dim = input_dim
        self.nclass_emotion = nclass_emotion

    def build_model(self):
        # Define model inputs
        mfcc_features = tf.placeholder(tf.float32, [None, max_sequence_length, input_dim])
        groundtruth_emotion = tf.placeholder(tf.int32, [None])
        keep_prob = tf.placeholder(tf.float32)

        # Encoder
        input_sequence = tf.split(tf.reshape(tf.transpose(mfcc_features, [1, 0, 2]), [-1, input_dim]), max_sequence_length, 0)
        encoder_cell_forward = rnn.core_rnn_cell.BasicLSTMCell(self.rnn_dim)
        encoder_cell_forward = rnn.core_rnn_cell.DropoutWrapper(encoder_cell_forward, output_keep_prob=keep_prob)
        encoder_cell_backward = rnn.core_rnn_cell.BasicLSTMCell(self.rnn_dim)
        encoder_cell_backward = rnn.core_rnn_cell.DropoutWrapper(encoder_cell_backward, output_keep_prob=keep_prob)
        rnn_outputs, state_forward, state_backward = rnn.static_bidirectional_rnn(encoder_cell_forward, encoder_cell_backward, input_sequence, dtype=tf.float32)
        state_forward = tf.concat([state_forward[0], state_forward[1]], axis=1)
        state_backward = tf.concat([state_backward[0], state_backward[1]], axis=1)
        state = tf.concat([state_forward, state_backward], axis=1)

        # Output layer emotion
        W_output_emotion = tf.Variable(tf.random_uniform([4*self.rnn_dim, self.nclass_emotion]))
        b_output_emotion = tf.Variable(tf.zeros([self.nclass_emotion]))
        outputs_emotion = tf.matmul(state, W_output_emotion) + b_output_emotion
        predict_emotion = tf.nn.softmax(outputs_emotion)

        # One hot for groundtruth
        groundtruth_emotion_onehot = tf.one_hot(groundtruth_emotion, nclass_emotion)

        # Cross entropy
        loss_emotion = tf.nn.softmax_cross_entropy_with_logits(logits = outputs_emotion, labels = groundtruth_emotion_onehot)
        #train_step = tf.train.AdamOptimizer(learning_rate).minimize(total_loss)
        loss_emotion = tf.reduce_mean(loss_emotion)
        train_step = tf.train.AdamOptimizer(learning_rate).minimize(loss_emotion)

        return mfcc_features, groundtruth_emotion, keep_prob, train_step, loss_emotion, predict_emotion

    def store_variables(self, sess, mfcc_features, groundtruth_emotion, keep_prob, train_step, loss_emotion, predict_emotion):
        self.sess = sess
        self.mfcc_features = mfcc_features
        self.groundtruth_emotion = groundtruth_emotion
        self.keep_prob = keep_prob
        self.train_step = train_step
        self.loss_emotion = loss_emotion
        self.predict_emotion = predict_emotion

def restore():
    # Restore
    sess = tf.Session()
    emotion_gender_recognizer = EmotionGenderRecognizer(rnn_dim, max_sequence_length, input_dim, nclass_emotion)
    mfcc_features, groundtruth_emotion, keep_prob, train_step, loss, predict_emotion = emotion_gender_recognizer.build_model()
    tf.train.Saver().restore(sess, tf.train.latest_checkpoint(model_dir))
    emotion_gender_recognizer.store_variables(sess, mfcc_features, groundtruth_emotion, keep_prob, train_step, loss, predict_emotion)

    return emotion_gender_recognizer

def classify_emotion(emotion_gender_recognizer, filepath):
    mfcc_features = []
    mfcc_features.append(np.load(filepath)[:max_sequence_length])
    feed_dict = {emotion_gender_recognizer.mfcc_features: mfcc_features, emotion_gender_recognizer.keep_prob: 1}
    prediction = emotion_gender_recognizer.sess.run(emotion_gender_recognizer.predict_emotion, feed_dict)

    return prediction[0]

def read_data(data):
    mfcc_features = []
    groundtruth_emotion = []
    for item in data:
        feature = np.load(feature_dir + item["filename"] + ".audio.npy")
        if max_sequence_length > feature.shape[0]:
            #feature = np.vstack([feature[:max_sequence_length], np.zeros((max_sequence_length-feature.shape[0], input_dim))])
            feature = np.vstack([np.zeros((max_sequence_length-feature.shape[0], input_dim)), feature[:max_sequence_length]])
        else:
            feature = feature[:max_sequence_length]
        mfcc_features.append(feature)
        groundtruth_emotion.append(emotion_table[item["label"]])

    return mfcc_features, groundtruth_emotion

if __name__ == "__main__":
    # Read data
    training_mfcc_features, training_groundtruth_emotion = read_data(training_data)
    testing_mfcc_features, testing_groundtruth_emotion = read_data(testing_data)

    # Build model
    sess = tf.Session()
    emotion_gender_recognizer = EmotionGenderRecognizer(rnn_dim, max_sequence_length, input_dim, nclass_emotion)
    mfcc_features, groundtruth_emotion, keep_prob, train_step, loss, predict_emotion = emotion_gender_recognizer.build_model()
    tf.global_variables_initializer().run(session = sess)

    # Train
    for epoch in range(nepoch):
        # Shuffle
        temp = list(zip(training_mfcc_features, training_groundtruth_emotion))
        random.shuffle(temp)
        training_mfcc_features, training_groundtruth_emotion = zip(*temp)

        for i in range(0, len(training_mfcc_features), batch_size):
            features = training_mfcc_features[i: i+batch_size]
            emotions = training_groundtruth_emotion[i: i+batch_size]

            feed_dict = {mfcc_features: features, groundtruth_emotion: emotions, keep_prob: dropout_rate}
            sess.run(train_step, feed_dict)

        training_loss = sess.run(loss, feed_dict)
        feed_dict = {mfcc_features: testing_mfcc_features, groundtruth_emotion: testing_groundtruth_emotion, keep_prob: 1}
        print("End of epoch " + str(epoch+1) + " : training_loss = " + str(training_loss) + ", testing_loss = " + str(sess.run(loss, feed_dict)))
        sys.stdout.flush()

    # Save model
    tf.train.Saver(max_to_keep=10).save(sess, model_path)
    print("Model successfully saved in " + str(model_path))

    # Use training data to test
    feed_dict = {mfcc_features: training_mfcc_features, groundtruth_emotion: training_groundtruth_emotion, keep_prob: 1}
    print("Training loss = " + str(sess.run(loss, feed_dict)))
    prediction_emotion = sess.run(predict_emotion, feed_dict)
    # Calculate accuracy of emotion
    correct_predict = 0
    for i, prediction in enumerate(prediction_emotion):
        predict = np.argmax(prediction)
        if int(predict) == int(training_groundtruth_emotion[i]):
            correct_predict += 1
    print("Accuracy of emotion = " + str(correct_predict*1.0/len(prediction_emotion)))

    # Test
    feed_dict = {mfcc_features: testing_mfcc_features, groundtruth_emotion: testing_groundtruth_emotion, keep_prob: 1}
    print("Testing loss = " + str(sess.run(loss, feed_dict)))
    prediction_emotion = sess.run(predict_emotion, feed_dict)
    # Calculate accuracy of emotion
    correct_predict = 0
    for i, prediction in enumerate(prediction_emotion):
        predict = np.argmax(prediction)
        if int(predict) == int(testing_groundtruth_emotion[i]):
            correct_predict += 1
    print("Accuracy of emotion = " + str(correct_predict*1.0/len(prediction_emotion)))

