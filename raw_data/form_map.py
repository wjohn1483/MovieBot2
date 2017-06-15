import json

mapping = {'警匪':'犯罪',
           '鬼':'恐怖',
           '驚悚':'懸疑',
           '搞笑':'喜劇',
           '歌舞劇':'音樂'}

with open('theater_type.json', 'w') as o:
  json.dump(mapping, o)
