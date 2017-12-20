# -*- coding: utf-8 -*-

import re
import numpy as np
import pandas as pd #导入Pandas
from sys import argv

print '本程序用于修正给付金额的信息值，按照关键字修正'
print '直接读取本目录下的jifujine_output.txt，并保存输出文件：jifujine_output.txt'

def fix_jifujine(jifujine, sentence_tmp):
    # 1 保险金额
    # 2 保险费
    # 3 账户价值
    # 4 现金价值
    # 5 豁免
    # 6 实际费用
    # 7 补贴额
    # 8 具体金额
    # 9 约定金额
    if jifujine > 0:
        ret = []

        # 1 保额 关键字
        kw = [u'保险金金额',u'基础保障金额',u'累积红利保险金额',u'每10000元基本保险金额给付500元',u'保险金额',u'额外保险金额',u'重大疾病保险金的3%',u'重大疾病保险金的50%',u'基本保险金额']
        for i in kw:
            if sentence_tmp.find(i) != -1:
                ret.append(1)
                break

        # 2 保险费 关键字
        kw = [u'保险费',u'保险费总额',u'趸缴保险费',u'累计保险费',u'累计所交保费',u'累计已交纳保险费',u'累计应交保险费',u'年交保险费',u'期交保险费',u'全部保险费',u'所交保费',u'所交保险费',u'所缴保险费',u'已付保险费',u'已交保费',u'已交保险费',u'已交的保险费',u'已交付的保险费',u'已交纳保险费',u'已交纳的保险费',u'已缴保险费',u'已支付的保险费',u'风险保险费',u'风险保障费',u'应交保险费总额',u'首次交纳保险费',u'首次交纳的保险费',u'首期保险费',u'实际已交纳保险费',u'本项责任保险费',u'实际交纳的保险费']
        for i in kw:
            if sentence_tmp.find(i) != -1:
                ret.append(2)
                break

        # 3 账户价值
        kw = [u'投资单位价值总额',u'投资账户',u'账户价值',u'账户余额',u'个人账户']
        for i in kw:
            if sentence_tmp.find(i) != -1:
                ret.append(3)
                break

        # 4 现金价值
        kw = [u'现金价值']
        for i in kw:
            if sentence_tmp.find(i) != -1:
                ret.append(4)
                break

        # 5 豁免
        kw = [u'豁免', u'免交', u'免予收取']
        for i in kw:
            if sentence_tmp.find(i) != -1:
                ret.append(5)
                break

        # 6 以上暂定为 6 其他        
        # 6 实际费用
        kw = [u'基本医疗费用',u'必要且合理的费用',u'初算费用',u'上述各项费用',u'实际费用',u'实际医疗费用',u'实际医药费用',u'手术费用',u'医疗费用',u'住院医疗费用']
        for i in kw:
            if sentence_tmp.find(i) != -1:
                ret.append(6)
                break

        # 7 补贴额
        kw = [u'每日补贴金额',u'每日补贴日额',u'每日住院补贴金额',u'每日住院津贴基数',u'住院津贴保险金日额']
        for i in kw:
            if sentence_tmp.find(i) != -1:
                ret.append(6)
                break

        # 8 具体金额
        match1 = re.search(ur'[0-9十百千万]+元', sentence_tmp)
        if match1 and sentence_tmp.find(u'较小者') == -1:
            ret.append(6)

        # 9 约定金额
        kw = [u'应给付的年金总额',u'对应的年领年金',u'约定的当期年金金额',u'约定的年领金额',u'约定的月领金额',u'基本年金金额',u'月度年金',u'约定的金额',u'申请的金额',u'年金金额',u'年领年金的金额',u'所得金额',u'附表约定',u'固定标准']
        for i in kw:
            if sentence_tmp.find(i) != -1:
                ret.append(6)
                break

        if 2 in ret and 5 in ret:
            ret_tmp = []
            for i in ret:
                if i != 2:
                    ret_tmp.append(i)
            ret = ret_tmp

        ret = list(set(ret))
        if len(ret)== 0:
            ret.append(-1)
        ret.sort()
        return ret
    else:
        return []

input_file_path = './jifujine_output.txt'
output_line_arr = []
if input_file_path.find(u'txt') != -1:
    input_file = open(input_file_path)
    for line in input_file.readlines():
        line = line.strip().decode('utf-8')
        line_info = line.split(u'|')
        if len(line_info) < 3:
            continue

        code = int(line_info[0])
        sentence = line_info[1]
        label = int(line_info[2])

        if label != 0:
            # print code, sentence
            fixed_label_arr = fix_jifujine(label, sentence)
            fixed_label = '+'.join([str(x) for x in fixed_label_arr])
        else:
            fixed_label = 0

        str_tmp = '%s|%s|%s\n' % (code, sentence, fixed_label)
        output_line_arr.append(str_tmp.encode('utf-8'))
else:
    print 'input file format error!'
    exit()

output_file = open('jifujine_output.txt', 'w')
for line in output_line_arr:
    output_file.write(line)
output_file.close()
