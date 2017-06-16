"""
    Author: Roy Lu
    Email: b01501061@gmail.com
    Utility: Extract Chinese time information in a sentence.
"""

import re
DEBUG = False

# For the variable end_time_hours
INTERVAL = 3

"""
    If you want to set your defualt hours for some specific words, such as "晚上" = 19 and "中午" = 12.
    You should modify three varibles "shift_hours_word", "shift_hours" and "default_hours" together.

    The varible shift_hours is for shifing time.
    For example, 
        晚上七點 --> 700 --> 700 + 1200 (shift time) --> 1900
"""
shift_hours_word = ["早上", "中午", "下午", "傍晚", "晚上" ,"凌晨", "午夜", "深夜", "早場", "午場", "晚場"]
shift_hours   = [ 0, 12, 12, 12, 12,  0, 0, 0, 0, 12, 12]
default_hours = [10, 11, 14, 17, 19, 23, 0, 0, 10, 11, 19]

day_begin_word = ["昨天", "明天", "今天", "後天", "大後天"]

shift_hours_dict = { c: i for i, c in zip(shift_hours, shift_hours_word) }
default_hours_dict =  { c: i for i, c in zip(default_hours, shift_hours_word) }

# 1st value of each tuple is for previous hours.
# 2nd value of each tuple is for next hours.
end_time_word = ["都可以", "都行", "以後", "以前", "左右"]
end_time_hours = [(INTERVAL, INTERVAL), (INTERVAL, INTERVAL), (0, INTERVAL), (INTERVAL, 0), (INTERVAL, INTERVAL)]
end_time_dict = { c: i for i, c in zip(end_time_hours, end_time_word) }

ch_num = ["零", "一", "二", "三", "四", "五",
          "六", "七", "八", "九", "十", "兩"]

ch2num_dict = { c: i for i, c in zip(list(range(0,11))+[2], ch_num) }

re_day_begin_word = "|".join(day_begin_word)
re_shift_hours_word = "|".join(shift_hours_word)
re_end_time_word = "|".join(end_time_word)
re_ch_num = "|".join(ch_num)

whole_time_pattern = "[%s]*[%s]*[%s|\d]+[點|:]*[%s|\d|半]*[分]*[%s]*" % ( re_day_begin_word,
                                                                          re_shift_hours_word,
                                                                          re_ch_num, 
                                                                          re_ch_num,
                                                                          re_end_time_word)
                                                                    
hour_num_pattern = "[%s|\d]+[點|:]*" % (re_ch_num)
minute_num_pattern = "[%s|\d|半]+[分]*" % (re_ch_num)
shift_hours_word_pattern = "(%s)" % (re_shift_hours_word)
end_time_pattern = "(%s)" % (re_end_time_word)

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

def extract_part_time_info(pattern, inp_string, dictionary):
    search_string = re.search(pattern, inp_string)
    if search_string:
        search_string = search_string.group(0)
        #dict_value = dictionary[search_string]

        # Replace shift_time string with ""
        inp_string = inp_string.replace(search_string, "")

    if DEBUG: print("pattern    = ", pattern)
    if DEBUG: print("search str = ", search_string)

    return search_string, inp_string

"""
    Args: 
        string: the natural language before inputing into NLU.

    Returns: (int time, str string)  
        1. time: the numerical time between 0000 and 2400. If there is no time infomation, return -1
        2. string: if time != -1, we will extract the time information in the string and return it.
                   however, if time == -1, we will return original string.
    E.g.
        Input  =  我想看明天午場09點半以後在華納威秀的電影
        Output =  {'start_time': 2130, 'end_time': 2359, 'modified_str': '我想看在華納威秀的電影'}
"""
def extract_time(string):

    # Get shift hours

    # Get time end
    end_time_string = re.search(end_time_pattern, string)
    if end_time_string:
        end_time_string = end_time_string.group(0)
        end_time = end_time_dict[end_time_string]

        # Replace shift_time string with ""
        string = string.replace(end_time_string, "")

    shift_hour_string, string = extract_part_time_info(shift_hours_word_pattern, string, shift_hours_dict)
    end_time_string, string = extract_part_time_info(end_time_pattern, string, end_time_dict)

    if DEBUG: print("whole_time_pattern = ", whole_time_pattern)

    # Get whole time
    time_string = re.search(whole_time_pattern, string)
    if DEBUG: print("time string = ", time_string)

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
    if not shift_hour_string and not time_string:
        return (-1, string)
    elif shift_hour_string and not time_string:
    # If there is only shift time information, return default hours according to shift time word.
        return (default_hours_dict[shift_hour_string], string)

    # Avoid incorrect time
    if shift_hour_string and hour < 12:
        hour = hour + shift_hours_dict[shift_hour_string]
    minute %= 60
    hour %= 24

    start_hour = end_hour = hour

    # Modify hour according to the end_time_word.
    if end_time_string:
        modify_time = end_time_dict[end_time_string]
        start_hour -= modify_time[0]
        end_hour += modify_time[1]
    else:
        end_hour += INTERVAL
    
    # Merge hour and minute into one number.
    ret_start_time = (start_hour % 24) * 100 + minute
    ret_end_time   = (end_hour % 24) * 100 + minute

    # Check if the end time is earlier than start time.
    # Namely, if the end time is in tomorrow.
    if ret_end_time < ret_start_time:
        ret_end_time = 2359

    return { 'start_time': ret_start_time, 'end_time': ret_end_time, 'modified_str': string }

if __name__ == "__main__":
    test_string = "我想看明天午場09點半以後在華納威秀的電影"
    ret = extract_time(test_string)
    print("Input  = ", test_string)
    print("Output = ", ret['start_time'], ret['end_time'], ret['modified_str'])
