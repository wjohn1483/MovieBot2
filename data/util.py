import re

pattern = '[鄉|市|鎮|區]'

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

