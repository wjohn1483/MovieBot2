import json
import random

class NLG:
    def __init__(self):
        self.template = json.load(open("./tables/NLG_templates.json", 'r'))

    def generate(self, action_dict):
        # For multiple return
        if (action_dict["act_type"] == "inform_movie_name") or \
                (action_dict["act_type"] == "inform_theater_name") or \
                (action_dict["act_type"] == "inform_showing_time") or \
                (action_dict["act_type"] == "inform_movie_showing") or \
                (action_dict["act_type"] == "request_movie_name") or \
                (action_dict["act_type"] == "request_theater_name") or \
                (action_dict["act_type"] == "request_showing_time"):
            index = random.randint(0, len(self.template[action_dict["act_type"]])-1)

            return self.template[action_dict["act_type"]][index] + str(action_dict["slot_value"])

        # For single return
        else:
            index = random.randint(0, len(self.template[action_dict["act_type"]])-1)
            slot_list = action_dict["slot_value"][0].keys()
            sentence = self.template[action_dict["act_type"]][index]
            for slot in slot_list:
                sentence = sentence.replace('{' + slot + '}', action_dict["slot_value"][0][slot])

            return sentence


        #if action_dict["act_type"] == "request_movie_name":
        #elif: action_dict["act_type"] == "request_theater_name":
        #elif: action_dict["act_type"] == "request_showing_time":
        #elif: action_dict["act_type"] == "inform_movie_showing":
        #elif: action_dict["act_type"] == "inform_movie_description":
        #elif: action_dict["act_type"] == "inform_movie_name":
        #elif: action_dict["act_type"] == "inform_movie_rating":
        #elif: action_dict["act_type"] == "inform_movie_type":
        #elif: action_dict["act_type"] == "inform_showing_time":
        #elif: action_dict["act_type"] == "inform_showing_version":
        #elif: action_dict["act_type"] == "inform_theater_address":
        #elif: action_dict["act_type"] == "inform_theater_location":
        #elif: action_dict["act_type"] == "inform_theater_name":
        #elif: action_dict["act_type"] == "inform_theater_phone":
        #elif: action_dict["act_type"] == "inform_theater_website":
        #elif: action_dict["act_type"] == "confirm":
        #elif: action_dict["act_type"] == "greeting":
