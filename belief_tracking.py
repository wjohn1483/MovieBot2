import numpy as np

class Belief_tracking():
  def __init__(self, initial_state):
    self.state = initial_state

  # update state and return slot needed to be confirmed 
  # slot_confirm is for multiple turns (action: confirm),
  # it returns a list of slots which are different from 
  # previous history
  def update_and_confirm(self, state, confirmed_slot = [], force_overwrite = True):
   
    slot_confirm = []
    
    if force_overwrite:
      self.state = state
    else:
      for n in self.state.keys():
        if self.state[n]:
          if self.state[n] != state[n] and n not in confirmed_slot:
            slot_confirm.append(n) 
          else:
            self.state[n] = state[n]
        else:
          self.state[n] = state[n] 
     
    return slot_confirm

  def reset_state(self):
    self.state = self.state.fromkeys(self.state, "")

  def get_state(self):
    return self.state

if __name__ == "__main__":
  t_1 = {1:"", 2:"",3:""}
  b = Belief_tracking(t_1)
  print(b.state)
  print(b.update_and_confirm({1:"d",2:"v",3:""}))
  print(b.state)  
  print(b.update_and_confirm({1:"s",2:"v",3:""}))
  print(b.state)
