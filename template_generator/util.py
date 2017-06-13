import re
import json

pattern = '[鄉|市|鎮|區]'
theater_info_slots = [ 'theater_address', 'theater_phone', 'theater_website' ]

def read_loc():
    filename = './data/loc.dict'

    dic = {}
    with open(filename, 'r') as f:
        for row in f:
            row = row.strip().split(' ')
            key = row[0]
            row2 = [ re.sub(pattern, '', word) for word in row[1:] ]
            row = list(set(row) | set(row2))
            
            dic[key] = row[1:]

    with open('loc.json', 'w', encoding='utf-8') as fout:
        json.dump(dic, fout, ensure_ascii=False, indent=4)

def gen_request_templates():
    
    cc = {
    # 地點
    'request':[{ 'intent': 'theater_location', 'slots': [''], 'mid_nls': ["在{intent}{%s}", "去{intent}{%s}", "{intent}{%s}"] },

    # 電影院的
    { 'intent': 'theater_name', 'slots': ['movie_name'], 'mid_nls': ["有放映{%s}的{intent}", "有播放{%s}的{intent}", "有{%s}的{intent}"] },

    # 地址
    { 'intent': 'theater_address', 'slots': ['movie_name'], 'mid_nls': ["{intent}{%s}"] },
    { 'intent': 'theater_phone', 'slots': ['movie_name'], 'mid_nls': ["{intent}{%s}"] },
    { 'intent': 'theater_website', 'slots': ['movie_name'], 'mid_nls': ["{intent}{%s}"] },

    # 時間
    { 'intent': 'showing_time', 'slots': ['movie_name', 'theater_name', ''], 'mid_nls': ["{%s}的{intent}", "{%s}的放映{intent}", 
                                                                                       "{%s}的播放{intent}", "{%s}放映{intent}", 
                                                                                       "{%s}播放{intent}"] },
    # 版本                                                                                    
    { 'intent': 'showing_version', 'slots': ['movie_name', ''], 'mid_nls': ["{%s}的{intent}", "{%s}的放映{intent}", 
                                                                          "{%s}的播放{intent}", "{%s}放映{intent}", 
                                                                          "{%s}播放{intent}"] },
    # 電影
    { 'intent': 'movie_name', 'slots': [''], 'mid_nls': ["最新的{intent}{%s}", "放映{intent}{%s}", 
                                                       "{%s}的播放{intent}", "{intent}{%s}"] },

    { 'intent': 'movie_country', 'slots': ['movie_name', ''], 'mid_nls': ["{intent}{%s}"] },
    { 'intent': 'movie_type', 'slots': ['movie_name', ''], 'mid_nls': ["{intent}{%s}"] }]
    }
    with open('./data/raw_request_template', 'w', encoding='utf-8') as fout:
        json.dump(cc, fout, ensure_ascii=False, indent=4)

def gen_inform_templates():
    
    cc = {
    # 地點
    'inform':[{ 'intent': 'theater_location', 'slots': ['theater_location'], 'mid_nls': ["{%s}"] },

    # 電影院的
    { 'intent': 'theater_name', 'slots': ['theater_name'], 'mid_nls': ["{%s}"] },

    # 時間
    { 'intent': 'showing_time', 'slots': ['showing_time'], 'mid_nls': ["{%s}"] },

    # 版本                                                                                    
    { 'intent': 'showing_version', 'slots': ['showing_version'], 'mid_nls': ["{%s}"] }, 

    # 電影
    { 'intent': 'movie_name', 'slots': ['movie_name'], 'mid_nls': ["{%s}"] },
    { 'intent': 'movie_country', 'slots': ['movie_country'], 'mid_nls': ["{%s}"] },
    { 'intent': 'movie_type', 'slots': ['movie_type'], 'mid_nls': ["{%s}"] } ]
    }

    with open('./data/raw_inform_template', 'w', encoding='utf-8') as fout:
        json.dump(cc, fout, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    gen_inform_templates()
    gen_request_templates()
