import os
import sys

import numpy as np
import scipy
import theano
import theano.tensor as T
from sklearn import preprocessing

from toolbox import load_model, id_to_seq, word_vs_id

import subprocess

sys.path.append('/data/home/andyyuan/Project/models')
#from baselines import seq_mean_encoding

batch_size = 1
frame = int(sys.argv[3])
#train_scp_file = sys.argv[1]
train_scp_file_list = sys.argv[1]
predict_path = sys.argv[2]

def file_len(filename):
  with open(filename,'r') as f:
    count = 0;
    for l in f.readlines():
        count += 1
  return count

def utt_data_gen(filename):
  X = []

  feat_proc = subprocess.Popen(['copy-feats scp:{} ark,t:- 2>/dev/null'.format(filename)],stdout=subprocess.PIPE,shell=True)


  start = False
  utt_count = 0
  processed_uttID = ""

  while True:
    if utt_count >= batch_size:
      yield (np.array(X),processed_uttID,utt_count)
      X = []
      utt_count = 0

    line = feat_proc.stdout.readline()
    line = line.rstrip('\n')
    if line == '':
      #end of the ark

      #shuffle scp file
      #close popoen and reopen a new one
      feat_proc.terminate()
      yield (np.array(X),processed_uttID,utt_count)
      break

    if '[' in line :
      assert(start == False)
      start = True

      processed_uttID = (line.split())[0].rstrip(".wav")

      continue

    if start == True and ']' not in line:
      #features
      feature = [float(s) for s in line.split()]
      X.append(feature)
      continue

    if ']' in line:
      #features
      feature = [float(s) for s in (line[:-1]).split()]
      X.append(feature)
      start = False
      utt_count += 1

def main():
    print 'loading data ...'
    dataset_dir = '/data/home/andyyuan/Datasets/speech'
    X_dev_file = os.path.join(dataset_dir, 'feature/apply_cmvn_dev_clean.ark')
    y_dev_file = os.path.join(dataset_dir, 'label/dev_clean/wd_align')
    X_test_file = os.path.join(dataset_dir, 'feature/apply_cmvn_test_clean.ark')
    y_test_file = os.path.join(dataset_dir, 'label/test_clean/wd_align')
    #predict_file = '/home_local/zyi870701/MTK_project/vec/0001_American_Beauty.fea'

    word_table = '/data/home/andyyuan/Datasets/speech/words.txt'

    word_id_21_30 = [2245, 4102, 4128, 4233, 4422, 4982, 6815, 8815, 14207, 14610, 16128, 16290, 16345, 18997, 20760, 25455, 38835, 38923, 43812, 43966, 49826, 53919, 60148, 60526, 61167, 61249, 62343, 62546, 64301, 65278, 66176, 66782, 71551, 73633, 77097, 78983, 80465, 83288, 83447, 83838, 84757, 86715, 89704, 94051, 95263, 96066, 99109, 101199, 109786, 114870, 117093, 119267, 119666, 120453, 122724, 130175, 132580, 137421, 143042, 145010, 153596, 155006, 156994, 161789, 164601, 164788, 165122, 174754, 176009, 178501, 182453, 186516, 190873, 194651, 194839, 196472, 196844, 196862, 196937, 198233, 198748]

    word_id_31_40 = [4447, 35043, 43850, 49768, 50000, 52673, 55931, 58111, 59410, 61829, 68720, 69687, 70659, 71768, 72499, 76523, 78840, 82325, 98010, 103906, 104446, 114954, 117475, 125580, 135523, 149201, 150679, 157235, 157250, 160826, 173045, 173048, 176404, 176412, 176794, 178931, 192823, 193071, 196872, 198390, 198423]

    word_id_41_50 = [2241, 6092, 14777, 43782, 59257, 65237, 76990, 92762, 99340, 100434, 103897, 107293, 112085, 113561, 121385, 124794, 132258, 154885, 154967, 158912, 168428, 176419, 176795, 178918, 184336, 193785, 194352, 194454, 196158]

    word_id_21_60 = [2241, 2245, 4102, 4128, 4233, 4422, 4447, 4982, 6092, 6815, 8815, 10599, 11147, 14207, 14610, 14777, 16128, 16290, 16345, 18997, 20760, 25455, 35043, 38835, 38923, 43782, 43812, 43850, 43966, 49768, 49826, 50000, 52673, 53919, 55931, 58078, 58111, 59257, 59410, 60148, 60526, 61167, 61249, 61829, 62343, 62546, 64301, 65237, 65278, 66176, 66782, 68720, 69687, 70659, 71456, 71551, 71768, 72499, 73633, 76523, 76990, 77097, 78840, 78983, 80465, 81252, 82325, 83288, 83301, 83447, 83838, 84757, 86715, 89704, 92762, 94051, 95263, 96066, 96204, 98010, 99109, 99340, 100434, 101199, 101895, 103732, 103897, 103906, 104446, 107293, 108527, 109786, 110794, 112085, 113561, 114870, 114954, 114985, 117093, 117435, 117475, 117967, 118994, 119267, 119666, 120453, 121343, 121385, 121877, 122724, 123102, 124794, 125580, 128199, 130175, 132258, 132580, 135523, 137421, 141994, 143042, 145010, 149201, 150679, 153596, 154885, 154967, 155006, 156994, 157235, 157250, 158912, 160826, 161789, 164601, 164788, 165122, 168428, 173045, 173048, 174754, 176009, 176404, 176412, 176419, 176775, 176794, 176795, 176922, 177066, 178501, 178918, 178931, 182453, 184336, 186516, 190873, 192823, 193071, 193785, 194352, 194454, 194651, 194839, 196158, 196472, 196844, 196862, 196872, 196937, 198233, 198390, 198423, 198748]

    # word_id_list = range(4, 200001)
    # return_id_list, X_train = id_to_seq(
    #     feature_file=X_dev_file,
    #     label_file=y_dev_file,
    #     word_id_list=word_id_list,
    #     n_range=[21, 60],
    #     flat=True
    # )

    # word_vs_id(return_id_list, word_table)

    # _, X_test = id_to_seq(
    #     feature_file=X_test_file,
    #     label_file=y_test_file,
    #     word_id_list=return_id_list,
    #     n_range=[0, 3500],
    #     flat=True
    # )
    """
    _, X_train_1 = id_to_seq(
        feature_file=X_dev_file,
        label_file=y_dev_file,
        word_id_list=[int(sys.argv[1])],
        n_range=[0, 3500],
        flat=True
    )

    _, X_test_1 = id_to_seq(
        feature_file=X_test_file,
        label_file=y_test_file,
        word_id_list=[int(sys.argv[1])],
        n_range=[0, 3500],
        flat=True
    )

    _, X_train_2 = id_to_seq(
        feature_file=X_dev_file,
        label_file=y_dev_file,
        word_id_list=[int(sys.argv[2])],
        n_range=[0, 3500],
        flat=True
    )

    _, X_test_2 = id_to_seq(
        feature_file=X_test_file,
        label_file=y_test_file,
        word_id_list=[int(sys.argv[2])],
        n_range=[0, 3500],
        flat=True
    )
    """
    # TODO: change here
    model_file = './material/models/lstmae.300.510.pkl'
    # model_file = './lstmae_31_40_400/lstmae.400.1700.pkl'
    # model_file = './lstmae_41_50_400/lstmae.400.2000.pkl'
    model = load_model(model_file)
    encode_model = theano.function(
        inputs=[model.input],
        outputs=model.h_vals[-1],
        name='encode_model'
    )
    with open(train_scp_file_list,'r') as f:
	    for train_scp_file in f:
		    train_scp_file = train_scp_file.strip()
		    train_generator = utt_data_gen(train_scp_file+'.mfcc.scp')


		    """
		    f_min, f_max = [-111.0143, 68.73878]

		    X_train_list_1 = []
		    for seq in X_train_1:
			X_train_list_1.append(
			    np.asarray(
				a=(seq - f_min) / (f_max - f_min) * 2 - 1,
				dtype=theano.config.floatX
			    )
			)

		    X_test_list_1 = []
		    for seq in X_test_1:
			X_test_list_1.append(
			    np.asarray(
				a=(seq - f_min) / (f_max - f_min) * 2 - 1,
				dtype=theano.config.floatX
			    )
			)

		    X_train_list_2 = []
		    for seq in X_train_2:
			X_train_list_2.append(
			    np.asarray(
				a=(seq - f_min) / (f_max - f_min) * 2 - 1,
				dtype=theano.config.floatX
			    )
			)

		    X_test_list_2 = []
		    for seq in X_test_2:
			X_test_list_2.append(
			    np.asarray(
				a=(seq - f_min) / (f_max - f_min) * 2 - 1,
				dtype=theano.config.floatX
			    )
			)
		    """
		    """
		    reconstruct_model = theano.function(
			inputs=[model.input],
			outputs=model.yr_vals,
			name='reconstruct_model'
		    )
		    """
		    # print X_train_1[0][-1]
		    # print (reconstruct_model(X_train_list_1[0])[-1] + 1) / 2 * (f_max - f_min) + f_min

		    # print X_test_1[0][-1]
		    # print (reconstruct_model(X_test_list_1[0])[-1] + 1) / 2 * (f_max - f_min) + f_min

		    utt_counts = file_len(train_scp_file)

		    counts = 0
		    #predict_f = open(predict_file, 'w')

		    while True:
			(X, processed_uttID, processed_utt) = train_generator.next()
			#f_min, f_max = [-111.0143, 68.73878]
			#len_X =  len(X) / 13
			rid = len(X) % (frame/5)
			X = X[:len(X)-rid]
			X = np.array(X, np.float32).reshape((frame/5),len(X)/(frame/5),13)
			X_train_list = []
			for seq in X:
				X_train_list.append(
					np.asarray(
					#a=(seq - f_min) / (f_max - f_min) * 2 - 1,
					a=seq,
					dtype=theano.config.floatX
					)
				)

			counts += processed_utt
			X_encoded = []
			for index in xrange(len(X_train_list)):
				x = encode_model(X_train_list[index])
				for _ in xrange(5):
					X_encoded.append(x)
			#predict_f.write("%s " % processed_uttID)
			predict_file = predict_path+"/"+processed_uttID+".audio.npy"
			predict_f = open(predict_file, 'wb')
			np.save(predict_f, X_encoded)
			#for x in X_encoded[0]:
			#	predict_f.write("%s " % x)
			#predict_f.write("\n")
			if (counts >= utt_counts):
				assert (counts == utt_counts)
				break
		    """
		    encode_train_1 = []
		    for index in xrange(len(X_train_list_1)):
			encode_train_1.append(encode_model(X_train_list_1[index]))
		    encode_test_1 = []
		    for index in xrange(len(X_test_list_1)):
			encode_test_1.append(encode_model(X_test_list_1[index]))
		    encode_train_2 = []
		    for index in xrange(len(X_train_list_2)):
			encode_train_2.append(encode_model(X_train_list_2[index]))
		    encode_test_2 = []
		    for index in xrange(len(X_test_list_2)):
			encode_test_2.append(encode_model(X_test_list_2[index]))
		    """
		    """
		    print '#(train-1): %d' % len(encode_train_1)
		    print '#(test-1): %d' % len(encode_test_1)
		    print '#(train-2): %d' % len(encode_train_2)
		    print '#(test-2): %d\n' % len(encode_test_2)

		    print 'in-sample:'
		    print '    cosine:'
		    print '        %s v.s. %s: %f' % (sys.argv[1], sys.argv[1], np.mean(1 - scipy.spatial.distance.pdist(encode_train_1, 'cosine')))
		    print '        %s v.s. %s: %f' % (sys.argv[2], sys.argv[2], np.mean(1 - scipy.spatial.distance.pdist(encode_train_2, 'cosine')))
		    print '    euclidean:'
		    print '        %s v.s. %s: %f' % (sys.argv[1], sys.argv[1], np.mean(scipy.spatial.distance.pdist(encode_train_1, 'euclidean')))
		    print '        %s v.s. %s: %f\n' % (sys.argv[2], sys.argv[2], np.mean(scipy.spatial.distance.pdist(encode_train_2, 'euclidean')))

		    print 'out-sample:'
		    print '    cosine:'
		    print '        %s v.s. %s: %f' % (sys.argv[1], sys.argv[1], np.mean(1 - scipy.spatial.distance.pdist(encode_test_1, 'cosine')))
		    print '        %s v.s. %s: %f' % (sys.argv[2], sys.argv[2], np.mean(1 - scipy.spatial.distance.pdist(encode_test_2, 'cosine')))
		    print '    euclidean:'
		    print '        %s v.s. %s: %f' % (sys.argv[1], sys.argv[1], np.mean(scipy.spatial.distance.pdist(encode_test_1, 'euclidean')))
		    print '        %s v.s. %s: %f\n' % (sys.argv[2], sys.argv[2], np.mean(scipy.spatial.distance.pdist(encode_test_2, 'euclidean')))

		    print 'in-sample:'
		    print '    cosine:'
		    print '        %s v.s. %s: %f' % (sys.argv[1], sys.argv[2], np.mean(1 - scipy.spatial.distance.cdist(encode_train_1, encode_train_2, 'cosine')))
		    print '    euclidean:'
		    print '        %s v.s. %s: %f\n' % (sys.argv[1], sys.argv[2], np.mean(scipy.spatial.distance.cdist(encode_train_1, encode_train_2, 'euclidean')))

		    print 'out-sample:'
		    print '    cosine:'
		    print '        %s v.s. %s: %f' % (sys.argv[1], sys.argv[2], np.mean(1 - scipy.spatial.distance.cdist(encode_test_1, encode_test_2, 'cosine')))
		    print '    euclidean:'
		    print '        %s v.s. %s: %f\n' % (sys.argv[1], sys.argv[2], np.mean(scipy.spatial.distance.cdist(encode_test_1, encode_test_2, 'euclidean')))

		    # for i in xrange(len(X_train_1)):
		    #     X_train_1[i] = preprocessing.scale(X_train_1[i])

		    # for i in xrange(len(X_train_2)):
		    #     X_train_2[i] = preprocessing.scale(X_train_2[i])

		    # TODO: Simple encoding baselines
		    encode_train_1_mean = []
		    for seq in X_train_1:
		    # for seq in X_train_list_1:
			encode_train_1_mean.append(seq_mean_encoding(seq))
		    encode_train_2_mean = []

		    for seq in X_train_2:
		    # for seq in X_train_list_2:
			encode_train_2_mean.append(seq_mean_encoding(seq))
		    print '\n%s v.s. %s: %f' % (sys.argv[1], sys.argv[1], np.mean(1 - scipy.spatial.distance.pdist(encode_train_1_mean, 'cosine')))
		    print '%s v.s. %s: %f' % (sys.argv[2], sys.argv[2], np.mean(1 - scipy.spatial.distance.pdist(encode_train_2_mean, 'cosine')))
		    print '%s v.s. %s: %f' % (sys.argv[1], sys.argv[2], np.mean(1 - scipy.spatial.distance.cdist(encode_train_1_mean, encode_train_2_mean, 'cosine')))
		    """

if __name__ == '__main__':
    main()
    print("Done")
