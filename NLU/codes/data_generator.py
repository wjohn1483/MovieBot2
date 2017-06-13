import json
import jieba
import random

percentage_of_training_data = 0.8

# Load dict
jieba.load_userdict("./tables/values.txt")

# Generate sentences with slots and intent
sentences = []
slots = []
intent = []
data = json.load(open("./data/nlu_data.json", 'r'))
for template in data:
    if "user" in template["nl"]:
        sentence = template["nl"]["user"]
    else:
        sentence = template["nl"]
    if template["values"] != None:
        sentence = sentence.replace("{" + template["slots"][0] + "}", template["values"])
    sentence = " ".join(jieba.cut(sentence))
    sentences.append(sentence)
    words = sentence.split()
    temp = ["O"] * len(words)
    for i, word in enumerate(words):
        if word == template["values"]:
            temp[i] = template["slots"][0]
    slots.append(" ".join(temp))
    intent.append(template["intent"])

# Shuffle
temp = list(zip(sentences, slots, intent))
random.shuffle(temp)
sentences, slots, intent = zip(*temp)

# Split data to training data and testing data
number_of_training_data = int(percentage_of_training_data * len(sentences))
training_sentences = sentences[:number_of_training_data]
training_slots = slots[:number_of_training_data]
training_intent = intent[:number_of_training_data]
testing_sentences = sentences[number_of_training_data:]
testing_slots = slots[number_of_training_data:]
testing_intent = intent[number_of_training_data:]

# Dump to json files
training_data = []
for i in range(len(training_sentences)):
    training_data.append({"sentence": training_sentences[i], "slots": training_slots[i], "intent": training_intent[i]})
testing_data = []
for i in range(len(testing_sentences)):
    testing_data.append({"sentence": testing_sentences[i], "slots": testing_slots[i], "intent": testing_intent[i]})
json.dump(training_data, open("./data/training_data.json", 'w'), indent=4)
json.dump(testing_data, open("./data/testing_data.json", 'w'), indent=4)
print("Total number of data = " + str(len(sentences)))
print("Number of training data = " + str(len(training_data)))
print("Number of testing data = " + str(len(testing_data)))

