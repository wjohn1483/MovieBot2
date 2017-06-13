import utils
import sys
sys.path.append('./NLU')
from NLU import NLU
from ontology import OntologyManager
from policy import PolicyManager

class DialogueManager():
  def __init__(self):
    self.nlu = NLU.NLU()
    self.OM = OntologyManager.OntologyManager()
    self.policy = PolicyManager.PolicyManager()

    self.system_state = {}.fromkeys(self.OM.get_all_slots(), '')
  def update(self, sentence):
    # remove date
    sentence = utils.block_date(sentence)
    print(sentence)
    # restore movie name
    sentence = utils.error_correction_by_nl(sentence)
    print(sentence)
    # NLU
    slot_dict, self.intent = self.nlu.understand(sentence)
    print(slot_dict)
    # restore slot value again
    slot_dict = utils.error_correction(slot_dict)
    # state tracking
    self.DialogueStateTracking(slot_dict)

    return self.policy.act_on((self.system_state, self.intent))

  # update DST
  def DialogueStateTracking(self, slot_dict):
    value_change = False
    for slot in slot_dict:
      if slot_dict[slot] != '':
        if self.system_state[slot] != '':
          value_change = True
        self.system_state[slot] = slot_dict[slot]

    return value_change

  def reset(self):
    self.slot_dict = {}.fromkeys(self.OM.get_all_slots(), '')

if __name__ == '__main__':
  DM = DialogueManager()
  while(True):
    s = input("> ")
    if s == 'reset':
      DM.reset()
    else:
      print(DM.update(s))


