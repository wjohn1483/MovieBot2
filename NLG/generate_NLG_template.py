import json
import collections

templates = collections.defaultdict(list)

# Multiple return
# request_movie_name
# index 0-4 for movie less than 5
templates["request_movie_name"].append("請問想要看哪一部電影呢？現在有的電影如下：\n")
templates["request_movie_name"].append("請問想看哪部呢？聽說有格調的人都看這些\n")
templates["request_movie_name"].append("請問想看哪個呢？大家都說這些電影好看！\n")
templates["request_movie_name"].append("請問想看哪個呢？智慧對話機器人很強的人似乎都看這些\n")
templates["request_movie_name"].append("請問想看哪個呢？聽說看這些電影的人後來都莫名拿書卷了\n")
# index 5-9 for movie more than 5
templates["request_movie_name"].append("請問想要看哪一部電影呢？我先列出五部給您參考：\n")
templates["request_movie_name"].append("請問想看哪一部呢？底下先列個五部看您喜不喜歡~\n")
templates["request_movie_name"].append("想要看哪部呢？由於數量過多所以我先列出五部喔：\n")
templates["request_movie_name"].append("符合條件的電影太多了！我先給您五部參考參考！\n")
templates["request_movie_name"].append("我先列出五部給您參考參考！：\n")

# request_theater_name
templates["request_theater_name"].append("想要在哪一間電影院看呢？\n")
templates["request_theater_name"].append("哪間電影院較符合您的需求呢？\n")

# request_showing_time
templates["request_showing_time"].append("請問想要在哪個時間看呢？這些時段目前還有位子~\n")

# inform_movie_showing
templates["inform_movie_showing"].append("底下這些滿足您的條件~\n")

# inform_movie_name
templates["inform_movie_name"].append("滿足您的條件的電影有\n")

# inform_theater_name
# # of theater less than 5
templates["inform_theater_name"].append("底下這些戲院有在上映\n")
templates["inform_theater_name"].append("情侶們好像常去這些地方看電影\n")
templates["inform_theater_name"].append("儂大和她老公似乎常去這些電影院看\n")
templates["inform_theater_name"].append("聽說這些電影院常有稀有的神奇寶貝出沒\n")
# # of theater more than 5
templates["inform_theater_name"].append("底下這些戲院有在上映，先列出五家給您參考參考：\n")
templates["inform_theater_name"].append("上映的戲院有點多，所以我先列出五家喔！\n")
templates["inform_theater_name"].append("這些戲院有上映你想看的電影，但是太多家了先列出一部份給您看看：\n")
templates["inform_theater_name"].append("底下這些戲院有在上映，礙於版面，先列個五家\n")

# inform_showing_time
templates["inform_showing_time"].append("這些時段還有位子，但所剩不多了，要搶要快！\n")
templates["inform_showing_time"].append("有這些時段可以選擇\n")

# Single return
# inform_movie_description
templates["inform_movie_description"].append("這部電影的敘述是{movie_description}")

# inform_movie_rating
templates["inform_movie_rating"].append("大家對這部電影的評分是{movie_rating}")

# inform_movie_type
templates["inform_movie_type"].append("這部是{movie_type}類型的電影喔，我也很喜歡{movie_type}類型的電影呢")
templates["inform_movie_type"].append("我個人認為是{movie_type}類型的電影")

# inform_showing_version
templates["inform_showing_version"].append("這部電影有{showing_version}的版本，要試試看嗎？")

# inform_theater_address
templates["inform_theater_address"].append("電影院位在{theater_address}")

# inform_theater_location
templates["inform_theater_location"].append("電影院在{theater_location}")

# inform_theater_phone
templates["inform_theater_phone"].append("電影院的電話是{theater_phone}，趕快打過去吧！")

# inform_theater_website
templates["inform_theater_website"].append("底下是電影院的網站連結，不要去到奇怪的網站喔\n{theater_website}")

# no_result
templates["no_result"].append("抱歉，沒有找到符合您條件的電影")

# confirm
templates["confirm"].append("您確定要訂{showing_time}在{theater_name}的{movie_name}嗎？")
templates["confirm"].append("跟您做個最後確認，要訂{showing_time}在{theater_name}的{movie_name}嗎？下好離手喔~")

# greeting
templates["greeting"].append("哈囉你好嗎 衷心感謝 珍重再見 期待再相逢")

# confuse
templates["confuse"].append("樓下支援黑人問號.jpg")
templates["confuse"].append("對不起，我沒有很懂您的意思")
templates["confuse"].append("對不起，這邊的訊號不好，沒有聽清楚您剛剛說什麼，可以麻煩再說得詳細一些嗎？")

json.dump(templates, open("./tables/NLG_templates.json", 'w'), indent=4)
