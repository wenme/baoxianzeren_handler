# -*- coding: utf-8 -*-

import pandas as pd
import re
from sys import argv 

print '本程序将step1.1的输出文件benefit_title_output.txt，按逗号分句并保留is_title的label'
print '参数一：benefit_title_output.txt'
print '输出文件：./test_data_set/benefit_title_output_splitted.txt'

# return 0: none bracket found
# return 1: left bracket more than right ones, to be concat
# return 2: right bracket more than left ones, to be closed
def concat_type(line):
    bracket_couple_arr = [
        (u'(', u')'),
        (u'（', u'）'),
        (u'[', u']'),
        (u'{', u'}')
    ]
    for bracket_couple in bracket_couple_arr:
        left = line.count(bracket_couple[0])
        right = line.count(bracket_couple[1])
        if left > right:
            return 1
        elif right > left:
            return 2
        else:
            pass
    return 0

def special_split(line, split_punctuation_arr):
    sub_sentence_arr = []
    str_buf = u''
    for i in line:
        if i in split_punctuation_arr:
            str_buf += i
            concat_type_tmp = concat_type(str_buf)
            if concat_type_tmp == 1:
                continue
            else:
                sub_sentence_arr.append(str_buf)
                str_buf = u''
        else:
            str_buf += i
    if len(str_buf) > 0:
        sub_sentence_arr.append(str_buf)
    return sub_sentence_arr

if argv[1].find(u'.txt') != -1:
    input_file = open(argv[1])
    output_line_arr = []
    for line in input_file.readlines():
        line = line.strip().decode('utf-8')
        line_info = line.split('|')

        if len(line_info) < 3:
            continue

        code = line_info[0]
        sentence = line_info[1]
        is_title = line_info[2]

        if not code.isdigit():
            continue

        sub_sentencese = special_split(sentence, [u',', u'，'])
        tmp_arr = []
        for sub_sentence in sub_sentencese:
            split_mark = ''
            if sentence.find(sub_sentence + u',') != -1:
                sub_sentence = sub_sentence + u','
            elif sentence.find(sub_sentence + u'，') != -1:
                sub_sentence = sub_sentence + u'，'
            else:
                # print 'ha?', sub_sentence
                pass

            line_tmp = '%s|%s|%s\n' % (code, sub_sentence, is_title)
            output_line_arr.append(line_tmp.encode('utf-8'))

    input_file.close()

    output_file = open('./test_data_set/benefit_title_output_splitted.txt', 'w')
    for line in output_line_arr:
        output_file.write(line)
    output_file.close()
else:
    print 'file format error!'
