from Levenshtein import distance
import numpy as np
from ontology import OntologyManager
import json

valid_slot = ['theater_address', 'theater_location', 'movie_name', \
              'movie_country', 'theater_name', 'movie_type']
time_map = {0:'零',1:'一',2:'兩',3:'三',4:'四',5:'五',6:'六',\
            7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二'}
subtime_map = {1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',\
               7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二'}

def error_correction(slot_dict, ontology): 
  for slot in slot_dict:
    if slot in valid_slot:
      value_list = ontology.values_by_slot(slot = slot)
      #print(value_list)

      similarity = [distance(s, slot_dict[slot]) for s in value_list]
      slot_dict[slot] = value_list[np.argmin(similarity)]

  return slot_dict
  
def time_transfer(string):
  if '：' in string or ':' in string:
    time = string.replace('：', '').replace(':', '')
  else:
    time = string
  #print(time)
  t = ''
  for c in time:
    if c.isdigit:
      t += c

  t = t[:4]
  if int(t) < 1200:
    o = '早上'
  elif int(t) == 1200:
    o = '中午'
  elif int(t) > 1200 and int(t) < 1800:
    o = '下午'
    t = str(int(t) - 1200)
    if len(t) < 4:
      t = '0' + t
  elif int(t) >= 1800: 
    o = '晚上'
    t = str(int(t) - 1200)
    if len(t) < 4:
      t = '0' + t
  
  o = o + time_map[int(t[0] + t[1])] + '點'
  if t[2] == '0' and t[3] != '0':
    o = o + subtime_map[int(t[3])] + '分'
  elif t[2] != '0' and t[3] == '0':
    o = o + subtime_map[int(t[2])] + '十分'
  elif t[2] != '0' and t[3] != '0':
    o = o + subtime_map[int(t[2])] + '十' + subtime_map[int(t[3])] + '分'

  return o

if __name__ == '__main__':

  OM = OntologyManager.OntologyManager()
  d = {'showing_time': '0015', 'movie_name': '我和他的季軍男友'}
  print(error_correction(d, OM))
  print(time_transfer('23:59'))
