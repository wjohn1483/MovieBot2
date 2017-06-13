import json
import copy
import sys
import re
import itertools

with open('./config', 'r') as f:
    path = f.readline().strip().split('=')[1]
    sys.path.append(path)

from ontology import OntologyManager

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



time_begin = ["早上", "中午", "下午", "晚上"]
ch_hours = ["一", "兩", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
num_hours = [ str(i) for i in range(1, 25) ]
ch_minutes = ["零分", "十分", "二十分", "三十分", "四十分", "五十分", "十五分", "二十五分", "三十五分", "四十五分", "五十五分"]
num_minutes = ["00", "10", "20", "30", "40", "50", "15", "25", "35", "45", "55"]

if __name__ == "__main__":

    filename = './data/template.json'
    loc_filename = './raw_data/loc.json'
    theater_name_filename = './raw_data/theater_name.json'

    # Generate time values
    begin_and_hour = [ "".join(list(l)) for l in list(itertools.product(time_begin, ch_hours)) ]
    time_values = [ "點".join(list(l)) for l in list(itertools.product(begin_and_hour, ch_minutes)) ]

    #time_values.extend(num_hours)
    #time_values.extend(time_begin[:4])
    #begin_and_hour = [ "".join(list(l)+[":"]) for l in list(itertools.product(time_begin, num_hours)) ]
    #time_values.extend([ "".join(list(l)) for l in list(itertools.product(begin_and_hour, minutes[1:-1])) ])

    # Location values
    loc_values = get_all_values(loc_filename, 'loc')
    theater_name_values = get_all_values(theater_name_filename, 'theater_name')

    ontologyManager = OntologyManager.OntologyManager()
    print(ontologyManager.get_all_slots())
    #ontologyManager.values_by_slot(slot=slot)
    print(ontologyManager.values_by_slot(slot='theater_location'))

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
        else:
            curr_values = values

        if slots[0] == '':
            template['values'] = None
            data.append(copy.deepcopy(template))
        else:
            for v in curr_values:
                template['values'] = v
                data.append(copy.deepcopy(template))
    nlu_data.extend(data)

    # request
    #data = []
    #for template in templates['request']:
    #    template['values'] = None
    #    data.append(copy.deepcopy(template))
    #nlu_data.extend(data)

    # booking
    data = []
    for template in templates['booking']:
        template['values'] = None
        data.append(copy.deepcopy(template))
    nlu_data.extend(data)

    # closing
    data = []
    for template in templates['closing']:
        template['values'] = None
        data.append(copy.deepcopy(template))
    nlu_data.extend(data)

    with open('./data/nlu_data.json', 'w', encoding='utf-8') as fout:
        json.dump(nlu_data, fout, ensure_ascii=False, indent=4)
