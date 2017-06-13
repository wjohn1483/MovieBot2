import itertools
import json
import os
import sys

theater_slots_name     = [ 'theater_location', 'theater_name' ]
theater_apw_slots_name = [ 'theater_address', 'theater_phone', 'theater_website' ]
movie_slots_name       = [ 'movie_name', 'movie_description', 'movie_rating' ]
showing_slots_name     = [ 'showing_time', 'showing_version' ]
movie_tc_slots_name    = [ 'movie_type', 'movie_country' ]

req_slots_dict = { 'theater_location': "地點", 
                   'theater_name': "電影院",
                   'theater_phone': "電話",
                   'theater_address': "地址",
                   'theater_website': "網址",
                   'movie_name': "電影", 
                   'movie_description': "介紹",
                   'movie_type': "類型",
                   'movie_rating': "評價",
                   'movie_country': "國家",
                   'showing_time': "時間",
                   'showing_version': "版本" }

nlg_begin_end_pair_1 = [ ["請問放映的", "有哪些？"], ["我想找", ""], ["我想要看", ""] ]
nlg_begin_end_pair_2 = [ ["我想找", ""], ["我要", ""], ["我想要", ""], ["我想要找", ""], ["找", ""], ["我想找", ""] ]
nlg_begin_end_pair_3 = [ ["", "片"], ["", "的電影"] ]
nlg_begin_end_pair_empty = [ ["", ""] ]

def gen_templates_by_slots_name(intent, slots_name, nlg_req_begin_end_pair, max_num_of_solts=float('inf')):
    ret = []
    for num_of_items in range(1, min(len(slots_name), max_num_of_solts) + 1, 1):
        print("Number of items: {}".format(num_of_items))
        for slots in itertools.combinations(slots_name, num_of_items):
            for nlg_req_begin, nlg_req_end in nlg_req_begin_end_pair:
                nlg = nlg_req_begin
                
                if intent == 'request':
                    slots_ch = [ req_slots_dict[s] for s in slots ]
                    if len(slots_ch) != 1:
                        slots_string = "、".join(slots_ch)
                    elif len(slots_ch) == 1:
                        slots_string = slots_ch[0]

                elif intent == 'inform':
                    slots_string = ",".join([ '{%s}' % slot for slot in slots ])

                nlg = nlg_req_begin + slots_string + nlg_req_end
                print(nlg)
                curr_intent = "_".join( [intent] + list(slots) )
                req = {'intent': curr_intent, 'slots': slots, 'nl': nlg}

                ret.append(req)
    return ret

# Generate request templates
print("Request Templates")
def gen_request_templates():

    # Generate template from slot1 mapping.
    request_templates = []

    request_templates.extend( gen_templates_by_slots_name( 'request', theater_slots_name, nlg_begin_end_pair_1, 1) )
    request_templates.extend( gen_templates_by_slots_name( 'request', theater_slots_name, nlg_begin_end_pair_empty, 1) )

    request_templates.extend( gen_templates_by_slots_name( 'request', theater_apw_slots_name, nlg_begin_end_pair_1, 1) )
    request_templates.extend( gen_templates_by_slots_name( 'request', theater_apw_slots_name, nlg_begin_end_pair_empty, 1) )

    request_templates.extend( gen_templates_by_slots_name( 'request', movie_slots_name + movie_tc_slots_name, nlg_begin_end_pair_2, 1) )
    request_templates.extend( gen_templates_by_slots_name( 'request', movie_slots_name + movie_tc_slots_name, nlg_begin_end_pair_empty, 1) )

    request_templates.extend( gen_templates_by_slots_name( 'request', movie_tc_slots_name, nlg_begin_end_pair_3, 1) )

    request_templates.extend( gen_templates_by_slots_name( 'request', showing_slots_name, nlg_begin_end_pair_2, 1) )
    request_templates.extend( gen_templates_by_slots_name( 'request', showing_slots_name, nlg_begin_end_pair_empty, 1) )

    # Customize
    request_templates.extend( gen_templates_by_slots_name( 'request', ['movie_rating'], 
                                                                      [ [ p[0], "%s的電影" % ch ] for p in nlg_begin_end_pair_2 + nlg_begin_end_pair_empty
                                                                        for ch in ["好", "壞", "普通", "還行", "非常好", "熱烈", "有趣", "兩極", "很好", "很差"] ], 1) )

    return request_templates

# Generate inform templates
def gen_inform_templates():
    print("Inform Templates")
    inform_templates = []

    inform_templates.extend( gen_templates_by_slots_name( 'inform', theater_slots_name, nlg_begin_end_pair_2, 1) )
    inform_templates.extend( gen_templates_by_slots_name( 'inform', theater_slots_name, nlg_begin_end_pair_empty, 1) )

    inform_templates.extend( gen_templates_by_slots_name( 'inform', showing_slots_name, nlg_begin_end_pair_2, 1) )
    inform_templates.extend( gen_templates_by_slots_name( 'inform', showing_slots_name, nlg_begin_end_pair_empty, 1) )

    inform_templates.extend( gen_templates_by_slots_name( 'inform', movie_tc_slots_name, nlg_begin_end_pair_2, 1) )
    inform_templates.extend( gen_templates_by_slots_name( 'inform', movie_tc_slots_name, nlg_begin_end_pair_3, 1) )
    inform_templates.extend( gen_templates_by_slots_name( 'inform', movie_tc_slots_name, nlg_begin_end_pair_empty, 1) )

    # Customize
    inform_templates.extend( gen_templates_by_slots_name( 'inform', ['theater_location'], 
                                                                    [ [ p[0], p1 ] for p in nlg_begin_end_pair_2 + nlg_begin_end_pair_empty 
                                                                      for p1 in ["附近", "附近的電影院", "附近的", "旁邊", "旁"] ], 1) )

    inform_templates.extend( gen_templates_by_slots_name( 'inform', ['movie_name'], nlg_begin_end_pair_2 + nlg_begin_end_pair_empty, 1) )

    return inform_templates

# Booking template


def gen_booking_template():
    booking_templates = []
    nlg_booking_templates = [ "請問可以幫我訂票嗎？", "幫我訂票", "訂", "訂吧"]
    booking = [ {'intent': 'booking', 'slots': [], 'nl': nlg_booking_template} for nlg_booking_template in nlg_booking_templates ]
    booking_templates.extend(booking)
    return booking_templates

# closing template


def gen_closing_templates():
    closing_templates = []
    nlg_success_templates = [ "謝謝", "謝謝你！" ]
    nlg_failure_template = "這不是我要的票．"
    #nlg_maxturn_template = "你已經成功考驗我的耐心了！"

    closing = [ {'intent': 'closing_success', 'slots': [], 'nl': nlg_success_template} for nlg_success_template in nlg_success_templates]
    failure = {'intent': 'closing_failure', 'slots': [], 'nl': nlg_failure_template}
    #maxturn = {'intent': 'closing_max_turn', 'slots': [], 'nl': {'user': nlg_maxturn_template}}

    closing_templates.extend(closing)
    closing_templates.append(failure)
    #closing_templates.append(maxturn)

    return closing_templates


def gen_irrelevant_templates():
    irrelevant_templates = []
    nlg_irrelevant_template = "跟我講{irrelevant}尬麻啦？"
    irrelevant = {'slots': [], 'nl': nlg_irrelevant_template}
    irrelevant_templates.append(irrelevant)
    return irrelevant_templates


if __name__ == "__main__":
    filename = './template.json'
    
    data = {}
    data['request'] = gen_request_templates()
    data['inform'] = gen_inform_templates()
    data['booking'] = gen_booking_template()
    data['closing'] = gen_closing_templates()
    #data['irrelevant'] = gen_irrelevant_templates()

    with open(filename, 'w', encoding='utf-8') as fout:
        json.dump(data, fout, ensure_ascii=False, indent=4)
