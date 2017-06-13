import itertools
import json
import os
import sys

slot2ch_dict = { 'theater_location': ["地點", "地方", "在哪裡", "在那裡"],
                 'theater_name': ["電影院", "戲院", "院", "影城"],
                 'theater_phone': ["電話", "手機", "客服", "聯絡方式", "聯絡", "號碼", "電話號碼", "手機號碼"],
                 'theater_address': ["地址", "位置", "在什麼路"],
                 'theater_website': ["網址", "網站"],
                 'movie_name': ["電影", "影片", "視頻"], 
                 'movie_description': ["介紹", "簡介", "內容", "大綱", "劇情", "內幕", "搶先看", "摘要", "重點"],
                 'movie_type': ["類型", "類別"],
                 'movie_rating': ["評價", "評分", "評論", "分數"],
                 'movie_country': ["國家", "出版商", "出版地", "製造地"],
                 'showing_time': ["時間"],
                 'showing_version': ["版本", "版"] }

begin_end_nls_iwant = [ ["我想", ""], ["我想要", ""], ["我想找", ""], ["我想要找", ""], ["請幫我找", ""], ["我要", ""], ["我要找", ""] ]
begin_end_nls_iwantin = [ ["我想在", ""], ["我想在", "看"], ["我想在", "看電影"], ["我想要在", ""], ["我想要在", "看"], ["我想要在", "看電影"] ]
begin_end_nls_igo   = [ ["我想去", ""], ["我要去", ""], ["我想要去", ""] ]
begin_end_nls_movie = [ ["請問放映的", "有哪些？"] ]
begin_end_nls_type_country = [ ["", "片"], ["", "的電影"] ]
begin_end_nls_empty = [ ["", ""] ]

def gen_templates(intent, slots, mid_nl, begin_end_nls):
    templates = []
    for begin, end in begin_end_nls:
        nl = begin + mid_nl + end
        template = { 'intent': intent,
                  'slots': slots,
                  'nl': nl }
        templates.append(template)
    return templates

def raw_template_to_nlu_template(filename, intent_type):
    with open(filename, 'r') as f:
        templates = json.load(f)

    ret_templates = []
    for template in templates[intent_type]:
        curr_intent = "%s_%s" % (intent_type, template['intent'])
        for mid_nl in template['mid_nls']:
            for slot in template['slots']:
                
                for slot_ch in slot2ch_dict[template['intent']]:
                    if slot == '':
                        curr_mid_nl = mid_nl.replace('{intent}', slot_ch).replace('{%s}','')
                    else:
                        curr_mid_nl = (mid_nl % slot).replace('{intent}', slot_ch)

                    if intent_type == 'request' and template['intent'] == 'theater_name':
                        ret_templates.extend(gen_templates(curr_intent, [slot], curr_mid_nl, begin_end_nls_igo))
                    if intent_type == 'request' and template['intent'] != 'theater_name':
                        ret_templates.extend(gen_templates(curr_intent, [slot], curr_mid_nl, begin_end_nls_iwant))


                    if intent_type == 'request' and ( template['intent'] == 'movie_name' or template['intent'] == 'movie_time' ):
                        ret_templates.extend(gen_templates(curr_intent, [slot], curr_mid_nl, begin_end_nls_iwant + begin_end_nls_movie))

                    if intent_type == 'request' and ( template['intent'] == 'movie_country' or template['intent'] == 'movie_type' ):
                        ret_templates.extend(gen_templates(curr_intent, [slot], curr_mid_nl, begin_end_nls_iwant))

                    if intent_type == 'inform':
                        ret_templates.extend(gen_templates(curr_intent, [slot], curr_mid_nl, begin_end_nls_iwant))

                    if intent_type == 'inform' and template['intent'] == 'theater_location':
                        ret_templates.extend(gen_templates(curr_intent, [slot], curr_mid_nl, begin_end_nls_iwantin))

                    # For empty
                    ret_templates.extend(gen_templates(curr_intent, [slot], curr_mid_nl, begin_end_nls_empty))

    return ret_templates

def gen_booking_template():
    booking_templates = []
    nlg_booking_templates = [ "請問可以幫我訂票嗎？", "幫我訂票", "訂", "訂吧"]
    booking = [ {'intent': 'booking', 'slots': [], 'nl': nlg_booking_template} for nlg_booking_template in nlg_booking_templates ]
    booking_templates.extend(booking)
    return booking_templates

# closing template
def gen_closing_templates():
    closing_templates = []
    nlg_failure_templates = [ "這不是我要的票",  "不是", "不", "否", "不對", "錯", "錯了", "不是這樣", "你很廢", "傻眼", "不好", "爛", "幹", "靠" ]
    failure = [ {'intent': 'closing_failure', 'slots': [], 'nl': nlg_failure_template} for nlg_failure_template in nlg_failure_templates ]
    closing_templates.extend(failure)
    return closing_templates

if __name__ == "__main__":
    filename = './data/template.json'

    data = {}
    data['request'] = raw_template_to_nlu_template('./data/raw_request_template', 'request')
    data['inform']  = raw_template_to_nlu_template('./data/raw_inform_template', 'inform')
    data['booking'] = gen_booking_template()
    data['closing'] = gen_closing_templates()

    with open(filename, 'w', encoding='utf-8') as fout:
        json.dump(data, fout, ensure_ascii=False, indent=4)
