import utils
import sys 
sys.path.append('./NLU')
from NLU import NLU
from ontology import OntologyManager

class DialogueManager():
  def __init__(self):
    self.nlu = NLU.NLU()
    self.OM = OntologyManager.OntologyManager()
    self.policy = None

    self.slot_dict = {}.fromkeys(self.OM.get_all_slots(), '')
  def Process_input(self, sentence):
    # remove date
    sentence = utils.block_date(sentence)
    print(sentence)
    # restore movie name
    sentence = utils.error_correction_by_nl(sentence)
    print(sentence)
    # NLU
    slot_dict, intent = self.nlu.understand(sentence)
    print(slot_dict)
    # restore slot value again
    slot_dict = utils.error_correction(slot_dict, self.OM)
    # state tracking
    self.DialogueStateTracking(slot_dict)

  # update DST
  def DialogueStateTracking(self, slot_dict):
    value_change = False
    for slot in slot_dict:
      if slot_dict[slot] != '':
        if self.slot_dict[slot] != '':
          value_change = True
        self.slot_dict[slot] = slot_dict[slot]

    return value_change    

  def Policy(self):
    pass

  def reset(self):
    self.slot_dict = {}.fromkeys(self.OM.get_all_slots(), '')

if __name__ == '__main__':
  DM = DialogueManager()
  while(True):
    s = input("> ")
    if s == 'exit':
      DM.reset()
    else:
      DM.Process_input(s)
      print(DM.slot_dict)
    
