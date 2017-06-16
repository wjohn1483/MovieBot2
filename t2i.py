import re

day_begin = ["昨天", "明天", "今天", "後天"]
#["禮拜一","禮拜二","禮拜三","禮拜四","禮拜五","禮拜六","禮拜天","禮拜日",
            #  "星期一","星期二","星期三","星期四","星期五","星期六","星期日","星期天",

time_begin = ["早上", "中午", "下午", "傍晚", "凌晨", "晚上", "午夜場"]
time_begin_int = [0, 1200, 1200, 1200, 0, 1200, 0]
time_begin_dict = { c: i for i, c in zip(time_begin_int, time_begin) }

time_end = ["都可以", "都行", "以後", "以前", "左右"]

ch_num = ["零", "一", "二", "三", "四", "五",
          "六", "七", "八", "九", "十", "兩"]

ch2num_dict = { c: i for i, c in zip(list(range(0,11))+[2], ch_num) }

re_day_begin = "|".join(day_begin)
re_time_begin = "|".join(time_begin)
re_time_end = "|".join(time_end)
re_ch_num = "|".join(ch_num)

whole_time_pattern = "[%s]*[%s]*(%s|\d)*(點|:)*[%s|\d|半]*(分)*(%s)*" % ( re_day_begin,
                                                                          re_time_begin,
                                                                          re_ch_num, 
                                                                          re_ch_num,
                                                                          re_time_end)
                                                                    
hour_num_pattern = "[%s|\d]+[點|:]*" % (re_ch_num)
minute_num_pattern = "[%s|\d|半]+[分]*" % (re_ch_num)
time_begin_pattern = "(%s)" % (re_time_begin)

string1 = "早上七點二十五分"
string2 = "2:00"
string3 = "2點"
string4 = "晚上都可以"
string5 = "早上十點四十以前"
string6 = "明天早上上3點半"

def get_int_num(string):
    int_nums = re.search("[\d]+", string)
    if int_nums:
        return int(int_nums.group(0))
    else:
        return False

def get_ch_num(string):
    ch_nums = re.search("[半]+", string)
    if ch_nums:
        return 30

    ch_nums = re.search("[%s]+" % re_ch_num, string)

    # Check if there is pattern in the input string.
    if not ch_nums:
        return False
    else:
        ch_nums = ch_nums.group(0)
    
    # Convert Chinese chars of a string into a list of digits.
    nums = []
    for s in ch_nums:
        nums.append(ch2num_dict[s])

    # Convert a list of digits into a number.
    if len(nums) == 1:
        ret = nums[0]
    elif len(nums) == 2:
        if nums[0] < 10:
            ret = nums[0] * 10 + nums[1]
        else: # if nums[0] == 10
            ret = nums[0] + nums[1]
    elif len(nums) == 3:
        ret = nums[0] * 10 + nums[2] 
    
    return ret

def time_ch2num(string):

    # Get whole time
    print("whole_time_pattern = ", whole_time_pattern)
    time_string = re.search(whole_time_pattern, string).group(0)
    print("time string = ", time_string)

    # Get time beginning words
    begining_words = re.search(time_begin_pattern, time_string)
    if begining_words:
        time_begin_dict[begining_words.group(0)]

    # Get hour
    hour = 0
    hour_string = re.search(hour_num_pattern, time_string)
    if hour_string:
        hour_string = hour_string.group(0)
        
        # Remove hour from origin string
        # In order to prevent from being selected when checking minutes.
        time_string = time_string.replace(hour_string, "")

        # Check if it is Chinese number first.
        # If not return false, then covert digit number to int.
        hour = get_ch_num(hour_string)
        if not hour:
            hour = get_int_num(hour_string)
    
    # Get minute
    minute = 0
    minute_string = re.search(minute_num_pattern, time_string)
    if minute_string:
        minute_string = minute_string.group(0)
        
        # Check if it is Chinese number first.
        # If not return false, then covert digit number to int.
        minute = get_ch_num(minute_string)
        if not minute:
            minute = get_int_num(minute_string)

    print("hour %d, minute %d" % (hour, minute))

if __name__ == "__main__":
    time_ch2num(string6)
    #ch2num("二十九")
