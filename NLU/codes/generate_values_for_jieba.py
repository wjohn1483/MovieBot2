import json

intent_table = []
values = []

data = json.load(open("./data/nlu_data.json", 'r'))
for template in data:
    if not (template["intent"] in intent_table):
        intent_table.append(template["intent"])
    if not (template["values"] in values):
        if template["values"] != None:
            values.append(template["values"].replace("：", "_"))

# Put all possible time into values
#date_begin = ["", "今天", "明天", "後天"]
#time_begin = ["", "早上", "中午", "下午", "晚上", "凌晨", "傍晚"]
#ch_hours = ["一", "兩", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
#num_hours = [str(i) for i in range(1, 25)]
#ch_hours.extend(num_hours)
#hour_unit = ["點"]
#ch_minutes = ["", "零", "十", "二十", "三十", "四十", "五十", "十五", "二十五", "三十五", "四十五", "五十五", "00", "10", "20", "30", "40", "50", "15", "25", "35", "45", "55"]
#minute_unit = ["", "分"]
#for date in date_begin:
#    for time in time_begin:
#        for hours in ch_hours:
#            for h_unit in hour_unit:
#                for minute in ch_minutes:
#                    for m_unit in minute_unit:
#                        value = time + date + hours + h_unit + minute + m_unit
#                        if not (value in values):
#                            values.append(value)

# Output intent to intent table
idx2indent = {}
for i, intent in enumerate(intent_table):
    idx2indent[i] = intent
json.dump(idx2indent, open("./tables/intent_table.json", 'w'), indent=4)

# Output values to file
output_file = open("./tables/values.txt", 'w')
for value in values:
    if value != None:
        output_file.write(str(value) + "\n")
