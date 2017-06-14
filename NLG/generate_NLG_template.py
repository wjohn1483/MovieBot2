import json
import collections

templates = collections.defaultdict(list)

# Multiple return
# request_movie_name
templates["request_movie_name"].append("請問想要看哪一部電影呢？現在有的電影如下：")

# request_theater_name
templates["request_theater_name"].append("想要在哪一間電影院看呢？底下這些戲院有上映喔")

# request_showing_time
templates["request_showing_time"].append("請問想要在哪個時間看呢？這些時段目前還有位子~")

# inform_movie_showing
templates["inform_movie_showing"].append("底下這些滿足您的條件~")

# inform_movie_name
templates["inform_movie_name"].append("滿足您的條件的電影有")

# inform_theater_name
templates["inform_theater_name"].append("底下這些戲院有在上映")

# inform_showing_time
templates["inform_showing_time"].append("這些時段還有位子，但所剩不多了，要搶要快！")

# Single return
# inform_movie_description
templates["inform_movie_description"].append("這部電影的敘述是{movie_description}")

# inform_movie_rating
templates["inform_movie_rating"].append("大家對這部電影的評分是{movie_rating}")

# inform_movie_type
templates["inform_movie_type"].append("這部是{movie_type}類型的電影喔")

# inform_showing_version
templates["inform_showing_version"].append("這部電影有{showing_version}的版本，要試試看嗎？")

# inform_theater_address
templates["inform_theater_address"].append("電影院位在{theater_address}")

# inform_theater_location
templates["inform_theater_location"].append("電影院在{theater_location}")

# inform_theater_phone
templates["inform_theater_phone"].append("電影院的電話是{theater_phone}，趕快打過去吧！")

# inform_theater_website
templates["inform_theater_website"].append("底下是電影院的網站連結，不要去到奇怪的網站喔{theater_website}")

# confirm
templates["confirm"].append("您確定要訂{showing_time}在{theater_name}的{movie_name}嗎？")

# greeting
templates["greeting"].append("哈囉你好嗎 衷心感謝 珍重再見 期待再相逢")

# confuse
templates["confuse"].append("樓下支援黑人問號.jpg")

json.dump(templates, open("./tables/NLG_templates.json", 'w'), indent=4)
