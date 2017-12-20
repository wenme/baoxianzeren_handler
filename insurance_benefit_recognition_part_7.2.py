# -*- coding: utf-8 -*-

from sys import argv
import re
import pandas as pd
import numpy as np

print '本程序用于更新目前已有的数据集<信息.xlsx>，使用程序前请先下载亿方云上面的最新<信息.xlsx>文件'
print '根据第一个"产品sheet"获取可更新的pid，即[信息抽取]值为0的pid。然后更新对应的"信息抽取的sheet"'
print '输入参数一：产品sheet的TXT文件'
print '输入参数二：信息抽取sheet的TXT文件'
print '输入参数三：aggregation_label_table_tmp.txt(上一步输出)'
print '输出aggregation_label_table_tmp.txt'

updated_pid_path = argv[1]
info_file_path = argv[2]
input_file_path = argv[3]
output_file_path = argv[3]

pid_to_be_updated = []
updated_pid_file = open(updated_pid_path)
for line in updated_pid_file.readlines():
    line = line.strip().decode('utf-8')
    line_info = line.split('|')

    if len(line_info) < 2:
        continue
    if line_info[0].isdigit() == False:
        continue

    updated_flag = int(line_info[1])
    if updated_flag == 0:
        pid_to_be_updated.append(int(line_info[0]))
updated_pid_file.close()

output_line_arr = []
str_tmp = 'pid|sentence|is_title|benefit_type|dengdaiqi|dengdaiqi_value|yuanyin|yuanyin_value|beibaorennianling|beibaorannianling_value|baodanniandu|baodanniandu_value|jifujine|jifujine_value|relation\n'
output_line_arr.append(str_tmp)

info_file = open(info_file_path)
for line in info_file.readlines():
    line = line.strip().decode('utf-8')
    line_info = line.split('|')

    if len(line_info) < 15:
        continue

    if line_info[0].isdigit() == True:
        pid = int(line_info[0])
        if pid not in pid_to_be_updated:
            output_line_arr.append('%s\n'%line.replace('| |', '||'))

input_file = open(input_file_path)
for line in input_file.readlines():
    line = line.strip().decode('utf-8')
    line_info = line.split('|')
    pid = line_info[0]

    if pid.isdigit() == True:
        if int(pid) in pid_to_be_updated:
            output_line_arr.append('%s\n'%line)
    else:
        print 'ha?', line
input_file.close()

output_file = open(output_file_path, 'w')
for line in output_line_arr:
    output_file.write(line.encode('utf-8'))
output_file.close()
