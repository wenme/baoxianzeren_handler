# -*- coding: utf-8 -*-

import pandas as pd
import re
from sys import argv

print '''
本程序将part1.2的输出文件(默认为'./test_data_set/benefit_title_output_splitted.txt')作为输入，基于保险金标题的判断保险金的类型，并保存到原文件。
输入参数一：./test_data_set/benefit_title_output_splitted.txt
输出：./test_data_set/benefit_title_output_splitted.txt
'''

def benefit_title_extractor(sentence):
    match = re.search(ur'[零一二三四五六七八九十百千]+ ', sentence)
    if match:
        sentence = sentence.replace(match.group(0), '')

    match = re.search(ur'[零一二三四五六七八九十百千]+、', sentence)
    if match:
        sentence = sentence.replace(match.group(0), '')

    match = re.search(ur'[0-9]+、', sentence)
    if match:
        sentence = sentence.replace(match.group(0), '')

    match = re.search(ur'[0-9\. ]+', sentence)
    if match:
        sentence = sentence.replace(match.group(0), '')

    matches = re.findall(ur'（.*?）', sentence)
    if len(matches) > 0:
        for match in matches:
            sentence = sentence.replace(match, '')

    return sentence.replace(':','')

def benefit_type_detector(sentence):
    # 医疗费用
    type_1_kw = [u'住院',u'癌症',u'紧急救援及转移',u'门急诊',u'门诊',u'手术',u'药品费',u'医疗',u'医药费',u'医院',u'重病监护',u'重大手术',u'重症',u'重症监护',u'转运回国']
    # 重大疾病
    type_2_kw = [u'重大疾病',u'特种疾病',u'癌症',u'白血病',u'第二类重大疾病',u'第一类重大疾病',u'恶性肿瘤',u'关爱',u'轻度重疾',u'轻症',u'轻症疾病',u'轻症重疾',u'特定恶性肿瘤',u'特定疾病',u'特定疾病|手术',u'现代病',u'严重疾病',u'原位癌',u'重大疾病',u'重疾']
    # 理财储蓄
    type_3_kw = [u'年金',u'安享返还',u'创业婚嫁',u'教育',u'老年',u'满期',u'生存',u'养老',u'祝福',u'祝寿']
    # 人寿意外
    type_4_kw = [u'身故',u'并发症',u'残疾',u'高残',u'高度残疾',u'特别关爱', u'生命关爱', u'后事处理',u'亲友前往处理',u'全残',u'伤残',u'身故',u'身故|残疾',u'身故|高残',u'身故|高度残疾',u'身故|全残',u'终末期']

    type_1_hit_str = u''
    for kw in type_1_kw:
        if kw.find('|') != -1:
            kw_arr = kw.split('|')
            found_flag = False
            for i in kw_arr:
                if sentence.find(i) == -1:
                    found_flag = False
                    break
                else:
                    found_flag = True
            if found_flag == True:
                type_1_hit_str += kw + '|'
        else:
            if sentence.find(kw) != -1:
                type_1_hit_str += kw + '|'


    type_2_hit_str = u''
    for kw in type_2_kw:
        if kw.find('|') != -1:
            kw_arr = kw.split('|')
            found_flag = False
            for i in kw_arr:
                if sentence.find(i) == -1:
                    found_flag = False
                    break
                else:
                    found_flag = True
            if found_flag == True:
                type_2_hit_str += kw + '|'
        else:
            if sentence.find(kw) != -1:
                type_2_hit_str += kw + '|'

    type_3_hit_str = u''
    for kw in type_3_kw:
        if kw.find('|') != -1:
            kw_arr = kw.split('|')
            found_flag = False
            for i in kw_arr:
                if sentence.find(i) == -1:
                    found_flag = False
                    break
                else:
                    found_flag = True
            if found_flag == True:
                type_3_hit_str += kw + '|'
        else:
            if sentence.find(kw) != -1:
                type_3_hit_str += kw + '|'

    type_4_hit_str = u''
    for kw in type_4_kw:
        if kw.find('|') != -1:
            kw_arr = kw.split('|')
            found_flag = False
            for i in kw_arr:
                if sentence.find(i) == -1:
                    found_flag = False
                    break
                else:
                    found_flag = True
            if found_flag == True:
                type_4_hit_str += kw + '|'
        else:
            if sentence.find(kw) != -1:
                type_4_hit_str += kw + '|'

    ret = u'无'
    hit_str_arr = [ret, type_1_hit_str, type_2_hit_str, type_3_hit_str, type_4_hit_str]
    max_pos = 0
    max_len = len(ret)
    for i in range(0, len(hit_str_arr)):
        if len(hit_str_arr[i]) > max_len:
            max_pos = i
            max_len = len(hit_str_arr[i])

    # return str(max_pos) if max_pos > 0 else ret
    return max_pos


input_file = open(argv[1])
sentence_arr = []
for line in input_file.readlines():
    line = line.decode('utf-8').replace('\n', '')
    sentence_arr.append(line)
input_file.close()

cur_benefit_type = 0
last_code = 0
output_file = open(argv[1], 'w')
for line in sentence_arr:
    line_info = line.split('|')
    if len(line_info) < 3:
        continue

    code = int(line_info[0])
    sentence = line_info[1]
    is_title = int(line_info[2])

    if code == last_code and is_title != 1:
        # line_tmp = '%s|%s|%s|%s\n' % (code, sentence, is_title, cur_benefit_type)
        line_tmp = '%s|%s|%s|%s\n' % (code, sentence, is_title, 0)
    elif code == last_code and is_title == 1:
        benefit_title_fixed = benefit_title_extractor(sentence)
        cur_benefit_type = benefit_type_detector(benefit_title_fixed)
        line_tmp = '%s|%s|%s|%s\n' % (code, benefit_title_fixed, is_title, cur_benefit_type)
    elif code != last_code and is_title != 1:
        cur_benefit_type = 0
        last_code = code
        # line_tmp = '%s|%s|%s|%s\n' % (code, sentence, is_title, cur_benefit_type)
        line_tmp = '%s|%s|%s|%s\n' % (code, sentence, is_title, 0)
    else:
        benefit_title_fixed = benefit_title_extractor(sentence)
        cur_benefit_type = benefit_type_detector(benefit_title_fixed)
        line_tmp = '%s|%s|%s|%s\n' % (code, benefit_title_fixed, is_title, cur_benefit_type)

    output_file.write(line_tmp.encode('utf-8'))

output_file.close()
