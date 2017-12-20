# -*- coding: utf-8 -*-

import re
import numpy as np
import pandas as pd
from sys import argv

def benefit_name_cleansing(benefit_name_arr):
    benefit_name_arr.sort(key=lambda x:x[0])
    ret = []
    
    for i in benefit_name_arr:
        pos1 = i[0]
        benefit_name1 = i[1]
        be_contained = False
        for j in benefit_name_arr:
            pos2 = j[0]
            benefit_name2 = j[1]
            if pos1 + len(benefit_name1) < pos2:
                continue
            if benefit_name2 != benefit_name1 and benefit_name2.find(benefit_name1) != -1:
                be_contained = True
                break

        if be_contained == False:
            ret.append(benefit_name1)

    return ret

def find_applying_docs(array, benefit_name_arr, benefit_applying_docs_arr):
    label_arr = []
    for i in array:
        label_arr.append(i[2])

    anchor_pos = 0
    start_pos = 0
    end_pos = 0
    for i in label_arr:
        if i == u'保险金申请标题':
            break
        anchor_pos += 1

    # find continous u'保险金申请资料', if finds no u'保险金申请资料' for over ten sentences, stop considering
    threshold = 10
    for i in range(anchor_pos, len(label_arr)):
        if array[i][2] == u'保险金申请资料' and threshold > 0:
            if start_pos == 0:
                start_pos = i
            end_pos = i
            thredhold = 10
        elif array[i][2] != u'保险金申请资料' and start_pos > 0 and threshold > 0:
            threshold -= 1
        elif threshold < 0:
            break
        else:
            pass

    # if could not find 保险金申请资料
    if anchor_pos == len(array) and start_pos == end_pos:
        return {}

    suspect_sentences = []
    for i in array[start_pos:end_pos+2]:
        if i[1].find(u'分期领取选择权') != -1:
            break
        suspect_sentences.append(i[1])

    ret = {}
    docs_tmp = []
    cur_benefit_str = u'默认保险金'
    for sentence in suspect_sentences:
        new_benefit_flag = False
        find_benefit_applying_docs_flag = False
        benefit_tmp = []

        for obj in benefit_name_arr:
            if sentence.find(obj) != -1:
                benefit_tmp.append((sentence.find(obj), obj))
                new_benefit_flag = True

        for obj in benefit_applying_docs_arr:
            if sentence.find(obj) != -1:
                find_benefit_applying_docs_flag = True
                break

        if new_benefit_flag == True and find_benefit_applying_docs_flag == True:
            benefit_tmp = benefit_name_cleansing(benefit_tmp)
            benefit_str_tmp = ','.join(benefit_tmp)

            if cur_benefit_str == u'默认保险金' and len(docs_tmp) == 0:
                cur_benefit_str = benefit_str_tmp
                docs_tmp.append(sentence)
                # print sentence, '1 1 init ++'
            elif sentence.find(u'：') == -1 or len(docs_tmp) == 0:
                if cur_benefit_str.find(benefit_str_tmp) != -1 or len(docs_tmp) > 0:
                    docs_tmp.append(sentence)
                    # print sentence, '1 1 ++'
                else:
                    cur_benefit_str = benefit_str_tmp
                    # print sentence, '1 1 change benefit'
            else:
                ret[cur_benefit_str] = docs_tmp
                # print 'start over:', cur_benefit_str, len(docs_tmp)
                cur_benefit_str = benefit_str_tmp
                docs_tmp = []
                docs_tmp.append(sentence)
                # print sentence, '1 1 so'
        elif new_benefit_flag == True and find_benefit_applying_docs_flag == False:
            benefit_tmp = benefit_name_cleansing(benefit_tmp)
            benefit_str_tmp = ','.join(benefit_tmp)

            if cur_benefit_str == u'默认保险金' and len(docs_tmp) == 0:
                cur_benefit_str = benefit_str_tmp
                # print sentence, '1 0 init'
            elif len(docs_tmp) == 0:
                if cur_benefit_str.find(benefit_str_tmp) != -1:
                    docs_tmp.append(sentence)
                    # print sentence, '1 0 ++'
                else:
                    cur_benefit_str = benefit_str_tmp
                    # print sentence, '1 1 change benefit'
            else:
                if cur_benefit_str.find(benefit_str_tmp) != -1:
                    docs_tmp.append(sentence)
                    # print sentence, '1 0 again ++'
                else:
                    ret[cur_benefit_str] = docs_tmp
                    # print 'start over:', cur_benefit_str, len(docs_tmp)
                    cur_benefit_str = benefit_str_tmp
                    docs_tmp = []
                    # print sentence, '1 0 so'
        elif new_benefit_flag == False and find_benefit_applying_docs_flag == True:
            docs_tmp.append(sentence)
            # print sentence, '0 1 ++'
        else:
            # print sentence, '0 0 pass'
            pass
        # print 'log: length of docs_tmp:', len(docs_tmp)

    ret[cur_benefit_str] = docs_tmp
    # print 'start over:', cur_benefit_str, len(docs_tmp)
    return ret

print '''
本程序用于提取条款的保险金申请资料(参考文件train/for_training_100_with_sentence_type_20170908.xlsx)，同时会利用本文件路径下的benefit_names_table和benefit_applying_documents_table，输出内容以条款为单位。注意：输入文件需经过深度学习分好类
'''

if len(argv) < 3:
    print('need 2 input parameters, the first one is source excel file path, the second one is output file path')
    exit()

excel_file = pd.read_excel(argv[1], header=0)
output_file = open(argv[2], 'w')
benefit_name_arr = []
benefit_applying_docs_arr = []

with open('benefit_names_table') as benefit_name_table_file:
    for line in benefit_name_table_file.readlines():
        line = line.replace('\n', '').strip()
        benefit_name_arr.append(line.decode('utf-8'))

with open('benefit_applying_documents_table') as benefit_applying_docs_table_file:
    for line in benefit_applying_docs_table_file.readlines():
        line = line.replace('\n', '').strip()
        benefit_applying_docs_arr.append(line.decode('utf-8'))

line_info = []
last_code = 0
for i in range(0, len(excel_file)):
    cur_code = excel_file['code'][i]
    if cur_code != last_code and len(line_info) > 0:
        ret = find_applying_docs(line_info, benefit_name_arr, benefit_applying_docs_arr)
        str_tmp = str(last_code) + '='*30 + '\n'
        if len(ret) == 0:
            str_tmp += u'无' + '\n'

        for k,v in ret.items():
            str_tmp += k + ':\n'
            for j in v:
                if j.find(u'核定') != -1:
                    continue
                str_tmp += '\t' + j + '\n'
        output_file.write(str_tmp.encode('utf-8'))
        line_info = []
        line_info.append((excel_file['code'][i], excel_file['sentence'][i], excel_file['label'][i]))
    else:
        line_info.append((excel_file['code'][i], excel_file['sentence'][i], excel_file['label'][i]))
    last_code = cur_code

# last documents would not be executed inside the loop
ret = find_applying_docs(line_info, benefit_name_arr, benefit_applying_docs_arr)
str_tmp = str(last_code) + '='*30 + '\n'
if len(ret) == 0:
    str_tmp += u'无' + '\n'
for k,v in ret.items():
    str_tmp += k + ':\n'
    for j in v:
        if j.find(u'核定') != -1:
            continue
        str_tmp += '\t' + j + '\n'
output_file.write(str_tmp.encode('utf-8'))
output_file.close()