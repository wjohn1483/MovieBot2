import json
import random
import utils

class NLG:
    def __init__(self):
        self.template = json.load(open("./tables/NLG_templates.json", 'r'))

    def _adjust_time(self, time):
        if len(time) == 1:
            return '00:0{}'.format(time)
        elif len(time) == 2:
            return '00:{}'.format(time)
        elif len(time) == 3:
            return '0{}:{}'.format(time[0], time[1:])
        else:
            return '{}:{}'.format(time[:2], time[2:])

    def generate(self, action_dict):
        # Adjust showing time
        if 'slot_value' in action_dict:
            for i, item in enumerate(action_dict["slot_value"]):
                if 'showing_time' in item:
                    action_dict['slot_value'][i]['showing_time'] = self._adjust_time(str(item["showing_time"]))

        # For multiple return
        if (action_dict["act_type"] == "inform_movie_showing"):
            index = random.randint(0, len(self.template[action_dict["act_type"]])-1)
            options = ""
            for item in action_dict["slot_value"]:
                options += "<br><span class='dialog-selection'>" + str(item["showing_time"]) + str("在") + str(item["theater_name"]) + str("的") + str(item["movie_name"]) + "</span>"

            return self.template[action_dict["act_type"]][index] + options

        elif (action_dict["act_type"] == "inform_theater_name") or \
                (action_dict["act_type"] == "request_theater_name"):
            index = random.randint(0, len(self.template[action_dict["act_type"]])-1)
            #slot_name = action_dict["slot_value"][0].keys()
            #for slot in slot_name:
            if action_dict["act_type"] == "inform_theater_name" and len(action_dict["slot_value"]) == 5:
                index = index + 4 if index < 4 else index
            options = ""
            for i in range(0, len(action_dict["slot_value"])):
                options += "<br><span class='dialog-selection'>" + str(action_dict["slot_value"][i]['theater_name']) + "</span>" + str(" (距離") +str(action_dict["slot_value"][i]['search_location'])+str(action_dict["slot_value"][i]['distance']) + str(")")

            return self.template[action_dict["act_type"]][index] + options

        elif (action_dict["act_type"] == "request_showing_time") or (action_dict["act_type"] == "inform_showing_time"):
            index = random.randint(0, len(self.template[action_dict["act_type"]])-1)
            slot_name = action_dict["slot_value"][0].keys()
            if action_dict["act_type"] == "request_movie_name" and len(action_dict["slot_value"]) == 5:
                index = index + 5 if index < 5 else index
            for slot in slot_name:
                time_list = []
                for i in range(len(action_dict["slot_value"])):
                    time_list.append(action_dict["slot_value"][i][slot])

            time_list = sorted(time_list)
            options = ""
            for t in time_list:
                options += "<br><span class='dialog-selection'>" + str(t) + "</span>"

            return self.template[action_dict["act_type"]][index] + options


        elif (action_dict["act_type"] == "inform_movie_name") or \
                (action_dict["act_type"] == "request_movie_name"):
            index = random.randint(0, len(self.template[action_dict["act_type"]])-1)
            slot_name = action_dict["slot_value"][0].keys()
            if action_dict["act_type"] == "request_movie_name" and len(action_dict["slot_value"]) == 5:
                index = index + 5 if index < 5 else index
            for slot in slot_name:
                options = ""
                for i in range(0, len(action_dict["slot_value"])):
                    options += "<br><span class='dialog-selection'>" + str(action_dict["slot_value"][i][slot]) + "</span>"

            return self.template[action_dict["act_type"]][index] + options

        # For single return
        else:
            index = random.randint(0, len(self.template[action_dict["act_type"]])-1)
            if action_dict["act_type"] == "no_result":
                return self.template[action_dict["act_type"]][index]

            if action_dict["act_type"] == "greeting":
                return self.template[action_dict["act_type"]][index]

            slot_list = action_dict["slot_value"][0].keys()
            sentence = self.template[action_dict["act_type"]][index]
            for slot in slot_list:
                sentence = sentence.replace('{' + slot + '}', str(action_dict["slot_value"][0][slot]))

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
