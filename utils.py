from Levenshtein import distance
import numpy as np
from ontology import OntologyManager
import json
import jieba
import re

jieba.load_userdict("./data/values.txt")

location_map = json.loads(open('raw_data/loc.json').read())
theater_map = json.loads(open('raw_data/theater_name.json').read())

edit_distance_threshold = 2

valid_slot = ['theater_address', 'movie_name', \
              'movie_country', 'movie_type']
time_map = {0:'零',1:'一',2:'兩',3:'三',4:'四',5:'五',6:'六',\
            7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二'}
subtime_map = {1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',\
               7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二'}
date_blacklist = ['禮拜一','禮拜二','禮拜三','禮拜四','禮拜五','禮拜六','禮拜天','禮拜日',\
                  '星期一','星期二','星期三','星期四','星期五','星期六','星期日','星期天']

OM = OntologyManager.OntologyManager()
value_list = []
for slot in valid_slot:
    value_list.extend(OM.values_by_slot(slot = slot))

def time_ch2num(string):
    pattern = "[早上|中午|下午|晚上]"
    time_begin = ["早上", "中午", "下午", "晚上"]
    num_begin = [0, 1200, 1200, 1200]
    ch_begin2num_begin_dic = { ch: num for ch, num in zip(time_begin, num_begin) }

    ch_hours = [ "零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二", "十三", "十四",
    "十五", "十六", "十七", "十八", "十九", "二十", "二十一", "二十二", "二十三", "二十四",
    "兩", "三十", "四十", "五十", "二十五", "三十五", "四十五", "五十五", "半"]
    num_hours = list(range(0, 25)) + [2, 30, 40, 50, 25, 35, 45, 55, 30]
    ch2num_dic = { ch: num for ch, num in zip(ch_hours, num_hours) }

    if not re.match("([早上|中午|下午|晚上])(.*)([點])(.*)([半|分])", string):
        return string

    for tb in time_begin:
        if tb in string:
            prefix_hour = ch_begin2num_begin_dic[tb]

    string = re.sub(pattern, '', string)

    # hour
    ch_hour = string.split("點")[0]
    num_hour = ch2num_dic[ch_hour] * 100 + prefix_hour

    # minute
    ch_minute = string.split("點")[1]
    num_minute = 0
    if len(ch_minute) != 0 and "分" in ch_minute[-1]:
        ch_minute = ch_minute[:-1]

    num_minute = ch2num_dic[ch_minute]
    return "%04d" % (num_hour + num_minute)

def error_correction(slot_dict):
  # name part
  for slot in slot_dict:
    if slot in valid_slot and slot_dict[slot] != '':
      value_list = OM.values_by_slot(slot = slot)
      #print(value_list)

      similarity = [distance(s, slot_dict[slot]) for s in value_list]
      slot_dict[slot] = value_list[np.argmin(similarity)]

  # location part
  for t in location_map:
    if slot_dict['theater_location'] in location_map[t]:
      slot_dict['theater_location'] = t
      break

  # theater name part
  if slot_dict['theater_name'] in theater_map:
    slot_dict['theater_name'] = theater_map[slot_dict['theater_name']]

  # Chinese time to number time
  if slot_dict['showing_time'] != '':
      slot_dict['showing_time'] = time_ch2num(slot_dict['showing_time'])

  return slot_dict

def block_date(sentence):
  for s in date_blacklist:
    if s in sentence:
      sentence = sentence.replace(s,'')
    if '/' in sentence:
      if sentence.index('/') in range(2, len(sentence) - 2):
        for i in [sentence.index('/')-2, sentence.index('/')-1]:
          if sentence[i].isdigit():
            pre = i
            break
        for i in [sentence.index('/')+2, sentence.index('/')+1]:
          if sentence[i].isdigit():
            aft = i
            break
        sentence = sentence.replace(sentence[pre:aft+1], '')
  return sentence

def error_correction_by_nl(string):
    words = " ".join(jieba.cut(string)).split()
    if ("戲院" in words) or ("影城" in words):
        return "".join(words)

    for sub_string_length in reversed(range(3, len(words))):
        for index in range(0, len(words)-sub_string_length+1):
            sub_string = "".join(words[index:index+sub_string_length])
            edit_distance = [distance(s, sub_string) for s in value_list]
            if np.min(edit_distance) <= edit_distance_threshold and np.min(edit_distance) != 0:
                temp = words[:index]
                temp.append(value_list[np.argmin(edit_distance)])
                temp.extend(words[index+sub_string_length+1:])
                words = temp
    return "".join(words)

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
    d = [{'showing_time': '0015', 'movie_name': '我和他的季軍男友'}]
    #print(block_date('我想要定7/25的票'))
    #print(error_correction(d, OM))
    #print(error_correction_by_nl("我想要看我和我的冠軍男友"))
    #print(error_correction_by_nl("我想要看神力女廢人"))
    print(error_correction_by_nl("我想要看神鬼戰士"))
    #print(time_transfer('23:59'))
