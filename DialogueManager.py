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
    self.unfinished_intent = ''
  def update(self, sentence):
    # remove date
    sentence = utils.block_date(sentence)
    #print(sentence)
    # restore movie name
    sentence = utils.error_correction_by_nl(sentence)
    #print(sentence)
    # NLU
    slot_dict, self.intent = self.nlu.understand(sentence)
    print('--------------------------------NLU Slot----------')
    utils.print_dict(slot_dict)
    print('--------------------------------NLU Intent--------')
    print(self.intent)
    # restore slot value again
    #slot_dict = utils.error_correction(slot_dict)
    utils.print_dict(slot_dict)
    # state tracking
    self.DialogueStateTracking(slot_dict)

    action_dict, self.unfinished_intent = self.policy.act_on(\
                               (self.system_state, self.intent, self.unfinished_intent))
    #action_dict = self.policy.act_on(\
    #                          (self.system_state, self.intent))
    print('--------------------------------System Action-----')
    print("Sys Act:    %s" % action_dict['act_type'])
    if 'slot_value' in action_dict:
        print("Slot-value:")
        for a in action_dict['slot_value']:
          print(a)
    if action_dict['act_type'] == 'confuse':
      for a in action_dict['slot_value'][0]:
        self.system_state[a] = ''

    print('--------------------------------Current State-----')
    utils.print_dict(self.system_state)
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
  print('你好  請問有什麼可以幫助您的嗎？')
  while(True):
    s = input("> ")
    print("#-#-#-#-#-# Turn %s #-#-#-#-#-#" % turn)
    print()
    print("# Input %s" % s)
    print()
    if s == 'reset':
      DM.reset()
      print('Dialogue State Has Beed Reset!')
      #print(DM.system_state)
      turn = 0
    elif s == 'end':
      exit()
    else:
      DM.update(s)

    print()
    print()
    turn += 1


