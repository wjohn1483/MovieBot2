import utils
import sys
sys.path.append('./NLU')
from NLU import NLU
from ontology import OntologyManager
from policy import PolicyManager

class DialogueManager():
  def __init__(self):
    self.nlu = NLU.NLU()
    self.policy = PolicyManager.PolicyManager()
    self.OM = OntologyManager.OntologyManager()

    self.system_state = {}.fromkeys(self.OM.get_all_slots(), '')
  def update(self, sentence):
    # remove date
    sentence = utils.block_date(sentence)
    #print(sentence)
    # restore movie name
    sentence = utils.error_correction_by_nl(sentence)
    #print(sentence)
    # NLU
    slot_dict, self.intent = self.nlu.understand(sentence)
    print('-----------------NLU slot-----------------')
    print(slot_dict)
    print('-----------------NLU intent-----------------')
    print(self.intent)
    # restore slot value again
    slot_dict = utils.error_correction(slot_dict)
    #print(slot_dict)
    # state tracking
    self.DialogueStateTracking(slot_dict)

    action_dict = self.policy.act_on((self.system_state, self.intent))
    print('-----------------action-----------------')
    print("Sys Act:    %s" % action_dict['act_type'])
    if 'slot_value' in action_dict:
        print("Slot-value: %s" % action_dict['slot_value'])
    if action_dict['act_type'] == 'confuse':
      for a in action_dict['slot_value'][0]:
        self.system_state[a] = ''

    print('-----------------current state-----------------')
    return self.system_state

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
    self.system_state = {}.fromkeys(self.OM.get_all_slots(), '')

if __name__ == '__main__':
  DM = DialogueManager()
  turn = 1
  print('安安   你真是他媽幹話王ㄟ')
  while(True):
    s = input("> ")
    print("# Turn %s" % turn)
    print("# Input %s" % s)

    if s == 'reset':
      DM.reset()
      print(DM.system_state)
      turn = 0
    elif s == 'end':
      exit()
    else:
      print(DM.update(s))

    print()
    print()
    turn += 1


