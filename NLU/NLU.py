import jieba
import json
import sys
sys.path.append("./codes/")
sys.path.append("./NLU/codes/")
import nlu_slot_filling_and_intent_prediction

# Load dict
jieba.load_userdict("./data/values.txt")

# Load slots and intents
idx2slot = json.load(open("./data/slots_table.json", 'r'))
idx2intent = json.load(open("./data/intent_table.json", 'r'))

class NLU:
    def __init__(self):
        self.slot_list = []
        for i in range(1, len(idx2slot)):
            self.slot_list.append(idx2slot[str(i)])
        self.sess, self.input_sentences, self.sequence_length, self.prediction_slot, self.prediction_intent = nlu_slot_filling_and_intent_prediction.restore()

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

if __name__ == "__main__":
    nlu = NLU()
    while True:
        sentence = input("> ")
        print(nlu.understand(sentence))
