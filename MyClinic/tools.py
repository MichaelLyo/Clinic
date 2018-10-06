import json
import datetime
import pytz

def parse_request_data(request):
    result = {}
    if request.method == 'POST':
        result = json.loads(request.body.decode('utf-8'))
    elif request.method == 'GET':
        result = request.GET
    return result


def parse_to_int(to_be_checked_item):
    if type(to_be_checked_item) == str:
        if to_be_checked_item and len(to_be_checked_item)>0:
            try:
                result = int(to_be_checked_item)
                return result
            except Exception as e:
                print('转换int出错，错误原因：',e)
                return 0
    elif type(to_be_checked_item) == int:
        return to_be_checked_item
    return 0



class DateEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            tz = pytz.timezone('Asia/Shanghai')
            new_time = obj.astimezone(tz)
            return new_time.strftime('%Y-%m-%d %H:%M')
        # elif isinstance(obj, date):
        #     return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


def single_get_first(unicode1):
    str1 = unicode1.encode('gbk')
    try:
        ord(str1)
        return str1.decode('gbk')
    except:
        asc = str1[0] * 256 + str1[1] - 65536
        if asc >= -20319 and asc <= -20284:
            return 'a'
        if asc >= -20283 and asc <= -19776:
            return 'b'
        if asc >= -19775 and asc <= -19219:
            return 'c'
        if asc >= -19218 and asc <= -18711:
            return 'd'
        if asc >= -18710 and asc <= -18527:
            return 'e'
        if asc >= -18526 and asc <= -18240:
            return 'f'
        if asc >= -18239 and asc <= -17923:
            return 'g'
        if asc >= -17922 and asc <= -17418:
            return 'h'
        if asc >= -17417 and asc <= -16475:
            return 'j'
        if asc >= -16474 and asc <= -16213:
            return 'k'
        if asc >= -16212 and asc <= -15641:
            return 'l'
        if asc >= -15640 and asc <= -15166:
            return 'm'
        if asc >= -15165 and asc <= -14923:
            return 'n'
        if asc >= -14922 and asc <= -14915:
            return 'o'
        if asc >= -14914 and asc <= -14631:
            return 'p'
        if asc >= -14630 and asc <= -14150:
            return 'q'
        if asc >= -14149 and asc <= -14091:
            return 'r'
        if asc >= -14090 and asc <= -13119:
            return 's'
        if asc >= -13118 and asc <= -12839:
            return 't'
        if asc >= -12838 and asc <= -12557:
            return 'w'
        if asc >= -12556 and asc <= -11848:
            return 'x'
        if asc >= -11847 and asc <= -11056:
            return 'y'
        if asc >= -11055 and asc <= -10247:
            return 'z'
        return ''


def get_str_first_letters(string):
    if string == None:
        return None
    lst = list(string)
    charLst = []
    for l in lst:
        charLst.append(single_get_first(l))
    return ''.join(charLst)

def round_up(value):
    # 替换内置round函数,实现保留2位小数的精确四舍五入
    return round(value * 100,2) / 100.0