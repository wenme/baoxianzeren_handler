# -*- coding: utf-8 -*-

import re
import numpy as np
import pandas as pd #导入Pandas
from sys import argv

print '本程序用于提取保单年度的信息值，如果包含中文数字会转换成阿拉伯数字'
print '输入参数一：包含保单年度标签的句子的excel文件或TXT文件'
print '输出文件：baodanniandu_output.txt'

def chs_digit_convertor_lt_9999(src_str):
    # 只支持10000以下的数字转换
    digit_map = {
        u''  : 1,
        u'零': 0,
        u'一': 1,
        u'二': 2,
        u'三': 3,
        u'四': 4,
        u'五': 5,
        u'六': 6,
        u'七': 7,
        u'八': 8,
        u'九': 9
    }

    ret = []
    # src_str split into two part: integral part and fractional part
    src_str_arr = src_str.split(u'点')
    if len(src_str_arr) == 1:
        s = src_str_arr[0]
        t = u'零'
    elif len(src_str_arr) == 2:
        s = src_str_arr[0]
        t = src_str_arr[1]
    else:
        return -1

    thousand_pos = s.find(u'千')
    hundred_pos = s.find(u'百')
    ten_pos = s.find(u'十')
    if thousand_pos != -1:
        ret.append(digit_map[s[:thousand_pos]])
        if hundred_pos != -1:
            ret.append(digit_map[s[thousand_pos+1:hundred_pos]])
            if ten_pos != -1:
                ret.append(digit_map[s[hundred_pos+1:ten_pos]])
                if ten_pos == len(s) - 1:
                    ret.append(0)
                else:
                    single_digit_str = s[ten_pos+1:]
                    if len(single_digit_str) == 0:
                        ret.append(0)
                    elif len(single_digit_str) == 1:
                        ret.append(digit_map[single_digit_str])
                    else:
                        single_digit_str = single_digit_str.replace(u'零', u'')
                        ret.append(digit_map[single_digit_str])
            else:
                ret.append(0)
                single_digit_str = s[hundred_pos+1:]
                if len(single_digit_str) == 0:
                    ret.append(0)
                elif len(single_digit_str) == 1:
                    ret.append(digit_map[single_digit_str])
                else:
                    single_digit_str = single_digit_str.replace(u'零', u'')
                    ret.append(digit_map[single_digit_str])

        else:
            ret.append(0)
            if ten_pos != -1:
                ret.append(digit_map[s[thousand_pos+1:ten_pos].replace(u'零', u'')])
                if ten_pos == len(s) - 1:
                    ret.append(0)
                else:
                    single_digit_str = s[ten_pos+1:]
                    if len(single_digit_str) == 0:
                        ret.append(0)
                    elif len(single_digit_str) == 1:
                        ret.append(digit_map[single_digit_str])
                    else:
                        single_digit_str = single_digit_str.replace(u'零', u'')
                        ret.append(digit_map[single_digit_str])
            else:
                ret.append(0)
                single_digit_str = s[thousand_pos+1:]
                if len(single_digit_str) == 0:
                    ret.append(0)
                elif len(single_digit_str) == 1:
                    ret.append(digit_map[single_digit_str])
                else:
                    single_digit_str = single_digit_str.replace(u'零', u'')
                    ret.append(digit_map[single_digit_str])

    else:
        ret.append(0)
        if hundred_pos != -1:
            ret.append(digit_map[s[:hundred_pos]])
            if ten_pos != -1:
                ret.append(digit_map[s[hundred_pos+1:ten_pos]])
                if ten_pos == len(s) - 1:
                    ret.append(0)
                else:
                    single_digit_str = s[ten_pos+1:]
                    if len(single_digit_str) == 0:
                        ret.append(0)
                    elif len(single_digit_str) == 1:
                        ret.append(digit_map[single_digit_str])
                    else:
                        single_digit_str = single_digit_str.replace(u'零', u'')
                        ret.append(digit_map[single_digit_str])

            else:
                ret.append(0)
                single_digit_str = s[hundred_pos+1:]
                if len(single_digit_str) == 0:
                    ret.append(0)
                elif len(single_digit_str) == 1:
                    ret.append(digit_map[single_digit_str])
                else:
                    single_digit_str = single_digit_str.replace(u'零', u'')
                    ret.append(digit_map[single_digit_str])

        else:
            ret.append(0)
            if ten_pos != -1:
                ret.append(digit_map[s[:ten_pos]])
                if ten_pos == len(s) - 1:
                    ret.append(0)
                else:
                    single_digit_str = s[ten_pos+1:]
                    if len(single_digit_str) == 0:
                        ret.append(0)
                    elif len(single_digit_str) == 1:
                        ret.append(digit_map[single_digit_str])
                    else:
                        single_digit_str = single_digit_str.replace(u'零', u'')
                        ret.append(digit_map[single_digit_str])

            else:
                ret.append(0)
                single_digit_str = s[:]
                if len(single_digit_str) == 0:
                    ret.append(0)
                elif len(single_digit_str) == 1:
                    ret.append(digit_map[single_digit_str])
                else:
                    single_digit_str = single_digit_str.replace(u'零', u'')
                    ret.append(digit_map[single_digit_str])

    if t == u'零':
        value = ret[0]*1000 + ret[1]*100 + ret[2]*10 + ret[3]
        return value
    else:
        fractional_part_str = u'0.'
        for i in t:
            fractional_part_str += str(digit_map[i])
        value = ret[0]*1000 + ret[1]*100 + ret[2]*10 + ret[3] + float(fractional_part_str)
        return value

def chs_digit_convertor(s):
    # 不支持亿或以上单位
    if s == u'两':
        return 2

    match = re.match(ur'(\d+)万', s)
    if match:
        return int(match.group(1)) * 10000

    match = re.match(ur'(\d+)千', s)
    if match:
        return int(match.group(1)) * 1000

    match = re.match(ur'(\d+)百', s)
    if match:
        return int(match.group(1)) * 100

    match = re.match(ur'(\d+)$', s)
    if match:
        return int(match.group(1))

    match = re.match(ur'(\d+)\.(\d+)$', s)
    if match:
        return float(s)

    if s.find(u'百分之') != -1: # 百分数
        ss = s[s.find(u'百分之')+3:]
        ret = chs_digit_convertor_lt_9999(ss)
        return float(ret)/100.0
    elif s.find(u'千分之') != -1: # 千分数
        ss = s[s.find(u'千分之')+3:]
        ret = chs_digit_convertor_lt_9999(ss)
        return float(ret)/1000.0
    elif s.find(u'分之') != -1:
        ss = s.split(u'分之')
        tmp1 = chs_digit_convertor_lt_9999(ss[0])
        tmp2 = chs_digit_convertor_lt_9999(ss[1])
        return float(tmp2)/float(tmp1)
    else:  # 非小数或百分数
        ss = s.split(u'万')
        # 中文数字以'万'、'亿'位为标志，前后的组织形式差不多
        if len(ss) == 1:
            ret = chs_digit_convertor_lt_9999(ss[0])
        elif len(ss) == 2:
            tmp1 = chs_digit_convertor_lt_9999(ss[0])
            tmp2 = chs_digit_convertor_lt_9999(ss[1])
            ret = tmp1*10000 + tmp2
        else:
            print 'you tell me what it is: %s' % s
            ret = -1
        return ret

quantifier_words = [u'个', u'周年', u'年']
training_file_path = argv[1]
output_line_arr = []
if training_file_path.find(u'.xlsx') != -1:
    excel_file = pd.read_excel(training_file_path, header=0, index=None)
    for i in range(0, len(excel_file)):
        code = excel_file['code'][i]
        sentence = excel_file['sentence'][i]
        label = excel_file['label'][i]
        value = ''
    
        # if code != 18:
        #     continue
    
        if label != 0:
            sentence = sentence.replace(' ', '')
            ret = []
            for word in quantifier_words:
                match = re.findall(ur'([首零一二三四五六七八九十百千万两]+)(%s)'%word, sentence)
                if len(match) > 0:
                    for i in match:
                        str_tmp = i[0]
                        if str_tmp == u'百' or str_tmp == u'千' or str_tmp == u'万':
                            continue
                        if str_tmp == u'首' and sentence.find(u'后的首个') == -1:
                            ret.append(1)
                        elif str_tmp != u'首':
                            ret.append(chs_digit_convertor(i[0]))
                        else:
                            pass
    
            if len(ret) == 0:
                for word in quantifier_words:
                    match = re.findall(ur'([0-9十百千万]+)(%s)'%word, sentence)
                    if len(match) > 0:
                        for i in match:
                            str_tmp = i[0]
                            if str_tmp == u'十' or str_tmp == u'百' or str_tmp == u'千' or str_tmp == u'万':
                                continue
                            ret.append(chs_digit_convertor(i[0]))
    
            if len(ret) == 0:
                if sentence.find(u'365日') != -1:
                    ret.append(1)
    
            ret = list(set(ret))
            ret.sort()
            value = ' '.join([str(x) for x in ret])
    
        str_tmp = '%s|%s|%s|%s\n' % (code, sentence, label, value)
        output_line_arr.append(str_tmp.encode('utf-8'))
elif training_file_path.find(u'txt') != -1:
    input_file = open(training_file_path)
    for line in input_file.readlines():
        line = line.strip().decode('utf-8')
        line_info = line.split(u'|')
        if len(line_info) < 3:
            continue

        code = int(line_info[0])
        sentence = line_info[1]
        label = int(line_info[2])
        value = ''

        # if code != 18:
        #     continue

        if label != 0:
            sentence = sentence.replace(' ', '')
            ret = []
            for word in quantifier_words:
                match = re.findall(ur'([首零一二三四五六七八九十百千万两]+)(%s)'%word, sentence)
                if len(match) > 0:
                    for i in match:
                        str_tmp = i[0]
                        if str_tmp == u'百' or str_tmp == u'千' or str_tmp == u'万':
                            continue
                        if str_tmp == u'首' and sentence.find(u'后的首个') == -1:
                            ret.append(1)
                        elif str_tmp != u'首':
                            ret.append(chs_digit_convertor(i[0]))
                        else:
                            pass

            if len(ret) == 0:
                for word in quantifier_words:
                    match = re.findall(ur'([0-9十百千万]+)(%s)'%word, sentence)
                    if len(match) > 0:
                        for i in match:
                            str_tmp = i[0]
                            if str_tmp == u'十' or str_tmp == u'百' or str_tmp == u'千' or str_tmp == u'万':
                                continue
                            ret.append(chs_digit_convertor(i[0]))

            if len(ret) == 0:
                if sentence.find(u'365日') != -1:
                    ret.append(1)

            ret = list(set(ret))
            ret.sort()
            value = ' '.join([str(x) for x in ret])

        str_tmp = '%s|%s|%s|%s\n' % (code, sentence, label, value)
        output_line_arr.append(str_tmp.encode('utf-8'))
else:
    print 'input file format error!'
    exit()

output_file = open('baodanniandu_output.txt', 'w')
for line in output_line_arr:
    output_file.write(line)
output_file.close()
