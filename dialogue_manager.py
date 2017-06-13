# -*- coding: utf-8 -*-
import jieba
from NLU import NLU
#from nlg import NLGManager
import belief_tracking
import sys
sys.path.append('./')
from policy import PolicyManager
import numpy as np

class Dialogue_manager():
  def __init__(self):
    # load initial slots
    self.initial_belief = {"movie_name": "",
                           "theater_name": "",
                           "showing_time": "",
                           "theater_location": "",
                           "theater_address": "",
                           "movie_type": "",
                           "movie_rating": "",
                           "theater_phone": "",
                           "movie_description": "",
                           "theater_website": "",
                           "movie_country": "",
                           "showing_version": ""}
    self.NLU = NLU.NLU()
   # self.NLG = NLGManager.NLGManager()
    self.belief_tracking = belief_tracking.Belief_tracking(self.initial_belief)
    self.policy_manager = PolicyManager.PolicyManager()

  #update belief state
  def update(self, string):
    
    r_dict = self.NLU.understand(string)
    #TODO comfirm
    self.belief_tracking.update_and_confirm(r_dict[0], force_overwrite=False)

  #def policy(self):
    self.action = self.policy_manager.act_on((self.belief_tracking.get_state(), r_dict[1]))
    return r_dict, self.action

  def sys_act(self):
    if self.action != "":
      return self.NLG.generate(self.action, "Movie")
      #return self.NLG.generate("moviename_str(美女與野獸)", "Movie")

if __name__ == '__main__':
  manager = Dialogue_manager()
  while(1):
    print("安安你好，有什麼能為您服務的呢？(reset可重來)")
    input_sentence = input("> ")
    if input_sentence == 'reset':
        print("又回到最初的起點~~~")
        print("")
        manager.belief_tracking.reset_state()
    else:
        nlu, sys_act = manager.update(input_sentence)
        print("=== NLU ===")
        print(nlu)
        print("")
        print("=== System Action ===")
        print(sys_act)
        print("")
    print("=== Belief Tracking ===")
    print(manager.belief_tracking.get_state())
    print("")
    #print(manager.policy())
    #print(manager.sys_act())
    print("")

