import json
import copy
import sys
import re
import random
import itertools

with open('./config', 'r') as f:
    path = f.readline().strip().split('=')[1]
    sys.path.append(path)

from ontology import OntologyManager

MAX_LIMIT = 800

def get_all_values(filename, val='loc'):
    with open(filename, 'r', encoding='utf-8') as fin:
        loc_dict = json.load(fin)
    values = []
    if val == 'loc':
        for v in loc_dict.values():
            values.extend(v)
    elif val == 'theater_name':
        values = list(loc_dict.keys())
    return values

def tup_list2str_list(tup_list, join_str=""):
    return [ join_str.join(list(t)) for t in tup_list ]

time_begin = ["早上", "中午", "下午", "晚上", "凌晨", "傍晚"]
week_begin = tup_list2str_list( list(itertools.product(["禮拜", ""], ["一", "二", "三", "四", "五", "六", "天"])) )
date_begin = ["今天", "明天", "後天"]

ch_hours = ["一", "兩", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
num_hours = [ str(i) for i in range(1, 25) ]
ch_minutes = ["", "零", "十", "二十", "三十", "四十", "五十", "十五", "二十五", "三十五", "四十五", "五十五"]
ch_minutes = tup_list2str_list( list(itertools.product(ch_minutes, ["", "分"])) )
num_minutes = ["00", "10", "20", "30", "40", "50", "15", "25", "35", "45", "55"]

rating_values = ["高", "低", "普通", "好", "棒", "超高", "超好", "超棒", "好棒棒", "熱門", "冷門"]

if __name__ == "__main__":

    filename = './data/template.json'
    loc_filename = './raw_data/loc.json'
    theater_name_filename = './raw_data/theater_name.json'

    # Generate time values
    hour_and_minute = tup_list2str_list(list(itertools.product(ch_hours, ch_minutes)), "點")
    #prefix_time = ( tup_list2str_list( list(itertools.product(week_begin, time_begin)) ) +
    #              tup_list2str_list( list(itertools.product(date_begin, time_begin)) ) + time_begin )
    prefix_time = (tup_list2str_list( list(itertools.product(date_begin, time_begin)) ) + time_begin )

    time_values = tup_list2str_list( itertools.product( tup_list2str_list( list(itertools.product(prefix_time, hour_and_minute)) ), ["", "看", "都可以"]) )

    #time_values.extend(num_hours)
    #time_values.extend(time_begin[:4])
    #begin_and_hour = [ "".join(list(l)+[":"]) for l in list(itertools.product(time_begin, num_hours)) ]
    #time_values.extend([ "".join(list(l)) for l in list(itertools.product(begin_and_hour, minutes[1:-1])) ])

    # Location values
    loc_values = get_all_values(loc_filename, 'loc')
    theater_name_values = get_all_values(theater_name_filename, 'theater_name')

    ontologyManager = OntologyManager.OntologyManager()
    #ontologyManager.values_by_slot(slot=slot)

    with open(filename, 'r', encoding='utf-8') as fin:
        templates = json.load(fin)

    nlu_data = []

    # inform
    data = []
    for template in templates['inform'] + templates['request']:

        slots = template['slots']

        if slots[0] != '':
            values = ontologyManager.values_by_slot(slot=slots[0])

        if slots[0] == 'theater_location':
            curr_values = loc_values
        elif slots[0] == 'showing_time':
            curr_values = time_values
        elif slots[0] == 'theater_name':
            curr_values = theater_name_values
        elif slots[0] == 'movie_country':
            head_values = [ v[0] for v in values ]
            curr_values = values + head_values
        elif slots[0] == 'movie_rating':
            curr_values = rating_values
        elif slots[0] == 'movie_type':
            curr_values.extend([""])
        else:
            curr_values = values

        # Filter too large values
        if len(curr_values) > MAX_LIMIT:
            curr_values = random.sample(curr_values, MAX_LIMIT)
        else:
            curr_values *= (MAX_LIMIT // len(curr_values))

        if slots[0] == '':
            template['values'] = None
            data.append(copy.deepcopy(template))
        else:
            for v in curr_values:
                template['values'] = v
                data.append(copy.deepcopy(template))
    nlu_data.extend(data)

    # greeting
    data = []
    for template in templates['greeting']:
        template['values'] = None
        data.append(copy.deepcopy(template))
    nlu_data.extend(data)

    # dontcare
    data = []
    for template in templates['dontcare']:
        template['values'] = None
        data.append(copy.deepcopy(template))
    nlu_data.extend(data)

    # booking
    """
    data = []
    for template in templates['booking']:
        template['values'] = None
        data.append(copy.deepcopy(template))
    nlu_data.extend(data)
    """

    # closing
    """
    data = []
    for template in templates['closing']:
        template['values'] = None
        data.append(copy.deepcopy(template))
    nlu_data.extend(data)
    """
    print("Total number of nlu data = %d" % len(nlu_data))

    with open('./data/nlu_data.json', 'w', encoding='utf-8') as fout:
        json.dump(nlu_data, fout, ensure_ascii=False, indent=4)
