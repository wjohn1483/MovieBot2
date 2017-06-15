import json

prediction = json.load(open("./NLU/prediction.json", 'r'))
testing_data = json.load(open("./data/testing_data.json", 'r'))

correct_prediction = 0
for i, item in enumerate(prediction):
    if prediction[i]["prediction_intent"] == testing_data[i]["intent"]:
        correct_prediction += 1

print("Intent accuracy = " + str(correct_prediction*1.0/len(prediction)))

