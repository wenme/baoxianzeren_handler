# -*- coding: utf-8 -*-

from sys import argv
import re

print '''
本程序基于part3的输出结果（默认为文件‘benefit_payment_type.txt’），对其benefit_payment_type字段进行序列统计给付方式数量，有如下原则：
0、剔除useful为0的句子，然后再考虑序列
1、一个属于金额3的句子需要有若干个属性为1或2的句子，才能构成一个给付情形
2、单独的3不做考虑
3、若干个1或2的句子后续连续的3，很大可能是属于“较大者”、“两者总和”之类的情形，所以只能判定为同一个给付情形
'''

if len(argv) < 2:
    print 'must specify an input document indicating sentences tagged with [benefit_payment_type]'
    exit()

def analyze_benefit_payment(array):
    sentence_tag_arr = []
    for obj in array:
        sentence = obj[0]
        benefit_payment_type = obj[1]
        sentence_tag_arr.append(benefit_payment_type)

    payment_count = 0
    tag_buf = []
    for i in sentence_tag_arr:
        if i == 1:
            payment_count += 1
            tag_buf = []
        elif i == 2:
            tag_buf.append(i)
        elif i == 3:
            if len(tag_buf) > 0:
                payment_count += 1
                tag_buf = []
            else:
                pass
        else:
            pass
    return payment_count

def analyze_document_benefit(array):
    rslt = []
    benefit_sentence_arr = []
    appending_flag = False
    cur_benefit_name = u'default benefit'
    for obj in array:
        code = obj[0]
        sentence = obj[1]
        is_title = obj[2]
        benefit_type = obj[3]
        useful = obj[4]
        benefit_payment_type = obj[5]

        if is_title == 0 and appending_flag == False:
            continue
        elif is_title == 0 and appending_flag == True:
            benefit_sentence_arr.append((sentence, benefit_payment_type))
        elif is_title == 1 and appending_flag == False:
            cur_benefit_name = sentence
            appending_flag = True
            benefit_sentence_arr.append((sentence, benefit_payment_type))
        else:
            ret = analyze_benefit_payment(benefit_sentence_arr)
            # TODO print ret
            rslt.append((cur_benefit_name, ret))
            benefit_sentence_arr = []
            benefit_sentence_arr.append((sentence, benefit_payment_type))
            cur_benefit_name = sentence

    # if no title of this liability of this document
    if len(benefit_sentence_arr) == 0:
        for obj in array:
            benefit_sentence_arr.append((obj[1], obj[5]))

    ret = analyze_benefit_payment(benefit_sentence_arr)
    # TODO print ret
    rslt.append((cur_benefit_name, ret))
    return rslt

input_file = open(argv[1])
first_line_flag = False
document_sentence_arr = []
cur_code = 0
for line in input_file.readlines():
    if first_line_flag == False:
        first_line_flag = True
        continue

    line = line.decode('utf-8').replace('\n', '')
    line_info = line.split('|')
    if len(line_info) < 6:
        continue

    code = int(line_info[0])
    sentence = line_info[1]
    is_title = int(line_info[2])
    benefit_type = line_info[3]
    useful = int(line_info[4])
    benefit_payment_type = int(line_info[5])

    if code != cur_code:
        if len(document_sentence_arr) > 0:
            ret = analyze_document_benefit(document_sentence_arr)
            # TODO print ret
            for i in ret:
                print cur_code, i[0]
                for j in i[1]:
                    print '情形'
        document_sentence_arr = []
        cur_code = code
    
    document_sentence_arr.append(code, sentence, is_title, benefit_type, useful, benefit_payment_type)

ret = analyze_document_benefit(document_sentence_arr)
# TODO print ret
for i in ret:
    print cur_code, i[0]
    for j in i[1]:
        print '情形'
