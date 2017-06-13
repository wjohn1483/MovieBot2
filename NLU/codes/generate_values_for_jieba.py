import json

intent_table = []
values = []

data = json.load(open("./data/nlu_data.json", 'r'))
for template in data:
    if not (template["intent"] in intent_table):
        intent_table.append(template["intent"])
    if not (template["values"] in values):
        values.append(template["values"])

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
