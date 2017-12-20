# -*- coding: utf-8 -*-

from sys import argv
import re

print '本程序为上一步输出aggragation_label_table.txt添加多一列数据，用于判断当连续出现给付金额时，判断是否出现“较大值”或“之和”等关系字眼'
print '0-没有关系，1-较大值，2-N者之和'
print '输出同样保存到原文件'

input_file_path = './aggregation_label_table.txt'
input_file = open(input_file_path)
input_line_arr = []
for line in input_file.readlines():
    line = line.strip().decode('utf-8')
    input_line_arr.append(line)
input_file.close()

input_line_arr.reverse()

output_file_path = './aggregation_label_table_tmp.txt'
last_label = '0'
scan_flag = False
output_line_arr = []
for line in input_line_arr:
    line_info = line.split('|')
    jifujine_label = line_info[-2]
    relation_flag = 0

    if jifujine_label.find(u'+') != -1:
        scan_flag = True
    elif jifujine_label != '0' and last_label != '0':
        scan_flag = True
    elif scan_flag == True and last_label == '0' and jifujine_label != '0':
        scan_flag = False
    else:
        pass

    if scan_flag == True and (line.find(u'较大值') != -1 or line.find(u'较大者') != -1 or line.find(u'较高者') != -1 or line.find(u'最大者') != -1):
        relation_flag = 1
    elif scan_flag == True and (line.find(u'两者之和') != -1 or line.find(u'二者之和') != -1):
        relation_flag = 2
    elif line_info[0] == 'pid':
        relation_flag = 'relation'
    else:
        ralation_flag = 0

    output_line_arr.append('%s|%s\n'%(line,relation_flag))
    last_label = jifujine_label

output_line_arr.reverse()
output_file = open(output_file_path, 'w')
for line in output_line_arr:
    output_file.write(line.encode('utf-8'))
output_file.close()
