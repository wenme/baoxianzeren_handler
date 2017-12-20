# -*- coding: utf-8 -*-

import re
import numpy as np
import pandas as pd #导入Pandas
from sys import argv

print '本程序用于提取事故原因的信息值，如果包含中文数字会转换成阿拉伯数字'
print '输入参数一：包含事故原因标签的句子的excel文件或TXT文件'
print '输出文件：yuanyin_output.txt'

def get_yuanyin(yuanyin_label, sentence_tmp):
    kw_arr = [
        ((u'意外伤害', u'意外事故'), u'意外'),
        ((u'航班',u'公共交通',u'交通工具',u'交通事故',u'民航',u'私家车',u'客运交通',u'公务车',u'客运交通工具',u'自驾车',u'公共交通工具',u'飞机',u'自驾汽车',u'火车',u'轮船',u'汽车',u'非营业车辆',u'客运机动车辆',u'客运列车',u'高铁',u'地铁',u'轻轨',u'出租车'), u'交通意外'),
        ((u'手术意外',u'介入诊疗意外',u'麻醉意外'), u'医疗意外'),
        ((u'突发急性病',u'患急性疾病',u'突发疾病'), u'突发病意外'),
        ((u'疾病'), u'疾病'),
        ((u'非因意外伤害',u'意外伤害事故以外',u'意外伤害以外'), u'非意外'),
        ((u'自然灾害',u'燃气',u'民用电',u'火灾',u'高空坠物',u'电梯',u'升降机',u'手扶电梯'),u'其他意外'),
    ]

    found_kw_arr = []
    for kws in kw_arr:
        kw_arr_tmp = kws[0]
        for kw in kw_arr_tmp:
            if sentence_tmp.find(kw) != -1:
                found_kw_arr.append(kw)

    kw_arr_reduced = []
    for i in found_kw_arr:
        contained_flag = False
        for j in found_kw_arr:
            if i == j:
                continue
            if j.find(i) != -1:
                contained_flag = True
                break
        if contained_flag == False:
            kw_arr_reduced.append(i)

    kw_arr_reduced = list(set(kw_arr_reduced))
    ret = []
    for kw in kw_arr_reduced:
        for kws in kw_arr:
            kw_arr_tmp = kws[0]
            if kw in kw_arr_tmp:
                ret.append(kws[1])
                break

    ret = list(set(ret))
    if yuanyin_label == 1:
        yuanyin_to_be_removed = [u'疾病', u'非意外']
        for i in yuanyin_to_be_removed:
            if i in ret:
                ret.remove(i)
    elif yuanyin_label == 2:
        yuanyin_to_be_removed = [u'意外', u'交通意外', u'医疗意外', u'突发病意外', u'其他意外']
        for i in yuanyin_to_be_removed:
            if i in ret:
                ret.remove(i)
    else:
        pass

    return ret

training_file_path = argv[1]
output_line_arr = []
if training_file_path.find(u'.xlsx') != -1:
    excel_file = pd.read_excel(training_file_path, header=0, index=None)
    for i in range(0, len(excel_file)):
        code = excel_file['code'][i]
        sentence = excel_file['sentence'][i]
        label = excel_file['label'][i]
        value = ''
    
        if label != 0:
            ret = get_yuanyin(label, sentence)
            ret = list(set(ret))
            value = '+'.join(ret)
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

        if label != 0:
            ret = get_yuanyin(label, sentence)
            value = '+'.join(ret)
        str_tmp = '%s|%s|%s|%s\n' % (code, sentence, label, value)
        output_line_arr.append(str_tmp.encode('utf-8'))
else:
    print 'input file format error!'
    exit()

output_file = open('yuanyin_output.txt', 'w')
for line in output_line_arr:
    output_file.write(line)
output_file.close()
