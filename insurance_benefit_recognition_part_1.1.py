# -*- coding: utf-8 -*-

import re

print '本程序修正step1的输出文件benefit_title_output.txt，将不可能的错误判断保险金title改回来'
print '输出文件：benefit_title_output.txt'

input_file = open('benefit_title_output.txt')
output_line_arr = []

for line in input_file.readlines():
    line = line.decode('utf-8')
    line_info = line.split('|')

    if len(line_info) < 3:
        continue

    pid = int(line_info[0])
    sentence = line_info[1]
    flag = int(line_info[2])

    # 排除包含“保险责任”的保险金title误判
    if flag == 1 and sentence.find(u'保险责任') != -1 and len(sentence) < 10:
        flag = 0

    sentence_tmp = sentence.strip().replace(u'（', '').replace(u'）', '').replace(u'、', '')
    sentence_tmp = re.sub(ur'^[0-9\.一二三四五六七八九十]', '', sentence_tmp)
    # 排除只有标点和数字序号的误判
    if flag == 1 and len(sentence_tmp) < 2:
        flag = 0

    output_line_arr.append('%s|%s|%s\n' % (pid,sentence,flag))
input_file.close()

output_file = open('benefit_title_output.txt', 'w')
for i in range(0, len(output_line_arr)-1):
    cur_line = output_line_arr[i]
    cur_match = re.search(ur'\|(\d)\n', cur_line)
    next_line = output_line_arr[i+1]
    next_match = re.search(ur'\|(\d)\n', next_line)
    #如果连续多个title，则只保留最后一个title的值，前面的都变成非title
    if cur_match.group(1) == '0':
        output_file.write(cur_line.encode('utf-8'))
    else:
        if next_match.group(1) == '1':
            cur_line = cur_line.replace(cur_match.group(0), '|0\n')
            output_file.write(cur_line.encode('utf-8'))
        else:
            output_file.write(cur_line.encode('utf-8'))
    # 倒数第二行，将最后一行也输出了
    if i == len(output_line_arr)-2:
        output_file.write(next_line.encode('utf-8'))
            
output_file.close()

# input_file = open('benefit_title_output.txt')
# last_pid = -1
# benefit_arr = []
# for line in input_file.readlines():
#     line = line.decode('utf-8')
#     line_info = line.split('|')
# 
#     if len(line_info) < 3:
#         continue
# 
#     pid = int(line_info[0])
#     sentence = line_info[1]
#     flag = int(line_info[2])
# 
#     if pid != last_pid and last_pid != -1:
#         if len(benefit_arr) > 0:
#             for benefit in benefit_arr:
#                 print '%s|%s' % (last_pid, benefit.encode('utf-8'))
#         else:
#             print '%s|无保险金' % last_pid
#         benefit_arr = []
# 
#     last_pid = pid
# 
#     if flag == 1:
#         benefit_arr.append(sentence)
# 
# if len(benefit_arr) > 0:
#     for benefit in benefit_arr:
#         print '%s|%s' % (last_pid, benefit.encode('utf-8'))
# else:
#     print '%s|无保险金' % last_pid
