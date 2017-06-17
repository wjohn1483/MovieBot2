import utils
import sys
sys.path.append('./NLU')
from NLU import NLU
from NLG import NLG
from ontology import OntologyManager
from policy import PolicyManager
from extract_time import extract_time

class DialogueManager():
  def __init__(self):
    self.nlu = NLU.NLU()
    self.nlg = NLG.NLG()
    self.policy = PolicyManager.PolicyManager()
    self.OM = OntologyManager.OntologyManager()

    self.system_state = {}.fromkeys(self.OM.get_all_slots(), '')
    self.system_state['showing_time_end'] = ''
    self.unfinished_intent = ''
    self.last_sys_act = ''

  def update(self, sentence):
    # remove date
    sentence = utils.block_date(sentence)
    #print(sentence)

    # restore movie name
    sentence = utils.error_correction_by_nl(sentence)
    
    # Extract time
    ret_dict = extract_time(sentence)
    print("ret_dict = ", ret_dict)
    sentence = ret_dict['modified_str']
    
    #print(sentence)
    # NLU
    slot_dict, self.intent = self.nlu.understand(sentence)
    print('--------------------------------NLU Slot----------')
    utils.print_dict(slot_dict)
    print('--------------------------------NLU Intent--------')
    # restore slot value again
    slot_dict = utils.error_correction(slot_dict)

    # correct time with previous extracting time
    if ret_dict['end_time'] != -1:
        # if user give the time twice: let end_time=start_time
        if self.system_state['showing_time'] == ret_dict['start_time']:
            slot_dict['showing_time_end'] = ret_dict['start_time']
        else:
            slot_dict['showing_time'] = ret_dict['start_time']
            slot_dict['showing_time_end'] = ret_dict['end_time']
        self.intent = 'inform_showing_time'

    print(self.intent)
    utils.print_dict(slot_dict)
    # state tracking
    self.DialogueStateTracking(slot_dict)

    action_dict, self.unfinished_intent = self.policy.act_on(\
                               (self.system_state, self.intent, self.unfinished_intent, self.last_sys_act))
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
    elif action_dict['act_type'] == 'no_result':
      self.reset()

    self.last_sys_act = action_dict['act_type']

    print('--------------------------------Current State-----')
    utils.print_dict(self.system_state)

    print('--------------------------------NLG sentence------')
    response = self.nlg.generate(action_dict)
    print(response)

    return action_dict, response

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
    self.system_state['showing_time_end'] = ''
    self.unfinished_intent = ''
    self.last_sys_act = ''

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


