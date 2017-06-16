import jieba
import json
import sys
import numpy as np
sys.path.append("./codes/")
sys.path.append("./NLU/codes/")
import nlu_slot_filling_and_intent_prediction

# For random forest
sys.path.append("./NLU/random_forest/")
#from helper_func import fromsentence2x, sid2ss, iid2is
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
import gzip, pickle, pdb, os
def load_pklgz( filename):
    print("... loading", filename)
    with gzip.open( filename, 'rb') as fp:
        u = pickle._Unpickler(fp)
        u.encoding = 'latin1'
        #obj = pickle.load(fp);
        obj = u.load()
    return obj;

# Load dict
jieba.load_userdict("./tables/values.txt")

# Load slots and intents
idx2slot = json.load(open("./tables/slots_table.json", 'r'))
idx2intent = json.load(open("./tables/intent_table.json", 'r'))

class NLU:
    def __init__(self):
        # Load RNN model
        self.slot_list = []
        for i in range(1, len(idx2slot)):
            self.slot_list.append(idx2slot[str(i)])
        self.sess, self.input_sentences, self.sequence_length, self.prediction_slot, self.prediction_intent = nlu_slot_filling_and_intent_prediction.restore()

        ## Load logistic regression
        #self.multi_target_forest_intent = load_pklgz("./NLU/random_forest/LU_intent.pkl.gz")
        #self.multi_target_forest_slot = load_pklgz("./NLU/random_forest/LU_slot.pkl.gz")

    def understand(self, sentence):
        # Create empty dict
        slot_value_dict = {}
        for slot in self.slot_list:
            slot_value_dict[slot] = ""

        sentence = " ".join(jieba.cut(sentence))
        sentence_slots, sentence_intent = nlu_slot_filling_and_intent_prediction.slot_filling_and_intent_prediction(sentence, self.sess, self.input_sentences, self.sequence_length, self.prediction_slot, self.prediction_intent)

        sentence = sentence.split()
        sentence_slots = sentence_slots.split()
        for i, slot in enumerate(sentence_slots):
            if slot in self.slot_list:
                slot_value_dict[slot] = sentence[i]

        return slot_value_dict, idx2intent[str(sentence_intent)]

    def understand_tree(self, sentence):
        sentence = " ".join(jieba.cut(sentence))
        print(sentence)
        x = fromsentence2x(sentence)
        #multi_target_forest_intent = load_pklgz("/media/wjohn1483/DATA/ntu/ICB/random_forest_original/LU_intent.pkl.gz")
        #multi_target_forest_slot = load_pklgz("/media/wjohn1483/DATA/ntu/ICB/random_forest_original/LU_slot.pkl.gz")
        intent = iid2is(self.multi_target_forest_intent.predict(x))
        slots = sid2ss(self.multi_target_forest_slot.predict(x))

        return slots, intent

if __name__ == "__main__":
    nlu = NLU()
    #while True:
    #sentence = input("> ")
    sentence = "我想要看神力女超人"
    print("="*15)
    print(nlu.understand(sentence))
    print("="*15)
    print(nlu.understand_tree(sentence))

