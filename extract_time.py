"""
    Author: Roy Lu
    Email: b01501061@gmail.com
    Utility: Extract Chinese time information in a sentence.
"""

import re
DEBUG = False

day_begin = ["昨天", "明天", "今天", "後天"]

"""
    If you want to set your defualt hours for some specific words, such as "晚上" = 19 and "中午" = 12.
    You should modify three varibles "shift_hours_word", "shift_hours" and "default_hours" together.

    The varible shift_hours is for shifing time.
    For example, 
        晚上七點 --> 700 --> 700 + 1200 (shift time) --> 1900
"""
shift_hours_word = ["早上", "中午", "下午", "傍晚", "晚上" ,"凌晨", "午夜", "深夜"]
shift_hours   = [ 0, 12, 12, 12, 12,  0, 0, 0]
default_hours = [10, 11, 14, 17, 19, 23, 0, 0]

shift_hours_dict = { c: i for i, c in zip(shift_hours, shift_hours_word) }
default_hours_dict =  { c: i for i, c in zip(default_hours, shift_hours_word) }

time_end = ["都可以", "都行", "以後", "以前", "左右"]

ch_num = ["零", "一", "二", "三", "四", "五",
          "六", "七", "八", "九", "十", "兩"]

ch2num_dict = { c: i for i, c in zip(list(range(0,11))+[2], ch_num) }

re_day_begin = "|".join(day_begin)
re_shift_hours_word = "|".join(shift_hours_word)
re_time_end = "|".join(time_end)
re_ch_num = "|".join(ch_num)

whole_time_pattern = "[%s]*[%s]*[%s|\d]+[點|:]*[%s|\d|半]*[分]*[%s]*" % ( re_day_begin,
                                                                          re_shift_hours_word,
                                                                          re_ch_num, 
                                                                          re_ch_num,
                                                                          re_time_end)
                                                                    
hour_num_pattern = "[%s|\d]+[點|:]*" % (re_ch_num)
minute_num_pattern = "[%s|\d|半]+[分]*" % (re_ch_num)
shift_hours_word_pattern = "(%s)" % (re_shift_hours_word)

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

"""
    Args: 
        string: the natural language before inputing into NLU.

    Returns: (int time, str string)  
        1. time: the numerical time between 0000 and 2400. If there is no time infomation, return -1
        2. string: if time != -1, we will extract the time information in the string and return it.
                   however, if time == -1, we will return original string.
    E.g.
        Input: 我想看明天午夜場03點半在華納威秀的電影
        Output: (330, '我想看在華納威秀的電影') 
"""
def extract_time(string):
        
    if DEBUG: print("time string = ", time_string)

    # Get time beginning words
    shift_time_string = re.search(shift_hours_word_pattern, string)
    if shift_time_string:
        shift_time_string = shift_time_string.group(0)
        shift_hour = shift_hours_dict[shift_time_string]

        # Replace shift_time string with ""
        string = string.replace(shift_time_string, "")

    if DEBUG: print("whole_time_pattern = ", whole_time_pattern)

    # Get whole time
    time_string = re.search(whole_time_pattern, string)

    # If there are time string
    hour = 0
    minute = 0
    if time_string:
        time_string = time_string.group(0)

        # Get hour
        hour_string = re.search(hour_num_pattern, time_string)
        if hour_string:
            hour_string = hour_string.group(0)
            
            # Remove hour from origin string
            # In order to prevent from being selected when checking minutes.
            rm_hour_time_string = time_string.replace(hour_string, "")

            # Check if it is Chinese number first.
            # If not return false, then covert digit number to int.
            hour = get_ch_num(hour_string)
            if not hour:
                hour = get_int_num(hour_string)
        
        # Get minute
        minute_string = re.search(minute_num_pattern, rm_hour_time_string)
        if minute_string:
            minute_string = minute_string.group(0)
            
            # Check if it is Chinese number first.
            # If not return false, then covert digit number to int.
            minute = get_ch_num(minute_string)
            if not minute:
                minute = get_int_num(minute_string)

        # Replace time string with ""
        string = string.replace(time_string, "")

    # If there is no time information, return -1.
    if not shift_time_string and not time_string:
        return (-1, string)
    elif shift_time_string and not time_string:
    # If there is only shift time information, return default hours according to shift time word.
        return (default_hours_dict[shift_time_string], string)

    # Avoid incorrect time
    if hour < 12:
        hour = hour + shift_hour
    minute %= 60
    hour %= 24

    if DEBUG: print("hour %d, minute %d" % (hour, minute))

    return (hour * 100 + minute, string)

if __name__ == "__main__":
    test_string = "我想看明天午夜場03點半在華納威秀的電影"
    t = extract_time(test_string)
    print(t)
