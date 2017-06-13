import json

filelist = ["./data/training_data.json", "./data/testing_data.json"]

word_list = []
word_list.append("_UNK")
for f in filelist:
    data = json.load(open(f, 'r'))
    for item in data:
        line = item["sentence"].split()
        for word in line:
            if not (word in word_list):
                word_list.append(word)


word_table = {}
for i, word in enumerate(word_list):
    word_table[word] = i

json.dump(word_table, open("./tables/word_table.json", 'w'), indent=4)
print("There are " + str(len(word_list)-1) + " words in the dataset")
