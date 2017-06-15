import os
import sys
import cPickle

import numpy as np
import theano
import theano.tensor as T
from sklearn import preprocessing

# sys.path.append('/project/andyyuan/speech-lab-project/models')
# sys.path.append('/home/syang100/speech-lab-project/models')
sys.path.append('/Users/Andy/Desktop/speech-lab-project/models')
from lstmae import LSTMAE

def id_to_seq(feature_file, label_file, word_id_list, n_range, flat=True):
    """ Given a list of word IDs, return the list of utterances
        that belong to the word_id_list.
    """
    f1 = open(feature_file, 'rb')
    f2 = open(label_file, 'rb')
    # TODO: handling word_id_list into dict, recording places and length.
    return_matrix = [[] for i in range(len(word_id_list))]
    word_index = {}
    start_order = []    # record the occurrence order of request word
    ind = 0
    current_seq = 0
    for id in word_id_list:
        word_index.update({id:ind})
        ind += 1
    for line in f2:
        tokens = line.strip().split()
        id = int(tokens[-1])
        start = int(tokens[1])
        leng = int(tokens[2])
        if id in word_id_list:
            start_order.append([tokens[0], start, leng, word_index[id], id])
        else: pass
    # now load the feature data to find the features for sequences
    ind = 0     # for current reading order of word_id_list w.r.t feature_file.
    seq_ind = ""
    start = -1
    leng = -1
    skip_seq = 0
    len_of_st = len(start_order)
    for line in f1:
        tokens = line.strip().split()
        if(skip_seq and len(tokens)>2):
            pos += 1
            continue
        else: skip_seq = 0
        if len(tokens) == 2:
            seq_ind = tokens[0] # new seq id
            pos = 0
            if(ind < len_of_st and seq_ind == start_order[ind][0]):
                id = start_order[ind][-1]           # requested word id
                start = start_order[ind][1]         # skip for "start" line in this seq.
                leng = start_order[ind][2]          # record for next len line from the start point.
                word_ind = start_order[ind][3]
                return_matrix[word_ind].append([])  # for a word's feature matrix of a seq.
            continue
        elif leng == 0 and len(tokens) > 2:         # different requested word maybe in the same seq.
            if(ind < len_of_st and seq_ind == start_order[ind][0]):
                id = start_order[ind][-1]
                start = start_order[ind][1] - pos
                leng = start_order[ind][2]
                word_ind = start_order[ind][3]
                return_matrix[word_ind].append([])  # for a word's feature matrix of a seq.
        if(ind < len_of_st and seq_ind != start_order[ind][0]):
            skip_seq = 1
            pos += 1
            continue
        if(start > 0):
            start -= 1
            pos += 1
            continue
        if(leng > 0):
            leng -= 1
            return_matrix[word_ind][-1].append([float(tokens[i]) for i in range(13)])
            if leng == 0:
                ind += 1    # next record order of word
            pos += 1
    f1.close()
    f2.close()
    # drop the word whose number of data
    # is not in range [n_min, n_max]
    seqs = []
    return_id_list = []
    n_min, n_max = n_range
    for i in xrange(len(return_matrix)):
        n_data = len(return_matrix[i])
        if n_data >= n_min and n_data <= n_max:
            seqs.append(return_matrix[i])
            return_id_list.append(word_id_list[i])
    if flat:
        # transform each utterance to an numpy.ndarray
        tmp = []
        for i in xrange(len(seqs)):
            for j in xrange(len(seqs[i])):
                tmp.append(np.array(seqs[i][j]))
        return return_id_list, tmp
    return return_id_list, seqs

def load_model(model_file):
    with open(model_file, 'rb') as f:
        model = cPickle.load(f)
    return model

def continue_train(model_file, X_train, X_test, n_epochs, learning_rate, save_steps, feature_range):
    model = load_model(model_file)
    model.train(
        X_train=X_train,
        X_test=X_test,
        n_epochs=n_epochs,
        learning_rate=learning_rate,
        save_steps=save_steps,
        feature_range=feature_range
    )

def word_vs_id(word_id_list, table):
    with open(table, 'rb') as f:
        for line in f:
            data = line.strip().split()
            assert len(data) == 2
            if int(data[-1]) in word_id_list:
                print data[0], data[-1]

def main():
    # TODO: specify /path/to/file of each datasets
    # dataset_dir = '/project/hoa/project'
    dataset_dir = '/Users/Andy/Desktop/Datasets/speech-word'
    # dataset_dir = '/home/syang100/Datasets'
    # X_train_file = os.path.join(dataset_dir, 'feature/apply_cmvn_train_clean_360.ark')
    # y_train_file = os.path.join(dataset_dir, 'label/train_clean_460/wd_align')
    X_dev_file = os.path.join(dataset_dir, 'feature/apply_cmvn_dev_clean.ark')
    y_dev_file = os.path.join(dataset_dir, 'label/dev_clean/wd_align')
    X_test_file = os.path.join(dataset_dir, 'feature/apply_cmvn_test_clean.ark')
    y_test_file = os.path.join(dataset_dir, 'label/test_clean/wd_align')
    # [word]    #(dev)    #(test)    [id]
    #  king        8         26     95318
    #  queen       8          8     142584
    #  man        88         67     107839
    #  woman      21         28     196472
    #  uncle       5          6     184060
    #  aunt        3          5     10068
    #  father     29         28     60526
    #  mother     32         32     117475
    # word_id_list = [95318, 142584, 184060, 10068, 60526, 117475]
    # TODO: change here
    word_id_list = range(4, 200001)
    return_id_list, train_data = id_to_seq(
        feature_file=X_dev_file,
        label_file=y_dev_file,
        word_id_list = word_id_list,
        n_range=[21, 30],
        flat=True
    )

    print train_data[0]
    print np.mean(train_data[-1], axis=0)
    print np.std(train_data[-1], axis=0)

    for i in xrange(len(train_data)):
        train_data[i] = preprocessing.scale(train_data[i])

    print train_data[0]
    print np.mean(train_data[-1], axis=0)
    print np.std(train_data[-1], axis=0)


if __name__ == '__main__':
    main()