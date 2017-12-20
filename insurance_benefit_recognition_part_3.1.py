# -*- coding: utf-8 -*-

from sys import argv

print '本程序用于修正事故原因的输出label'
print '如果保险金标题包含“意外”两字，则下面句子所有非0的label都变成1，否则保持不变，结果保存到yuanyin_output_tmp.txt'
print '需要一个匿名参数，不参与任何计算过程。由于发现修正后会有影响，所以step3.1可以考虑先跳过'

print '你输入了一个随机参数：', argv[1]
benefit_title_file = 'test_data_set/benefit_title_output_splitted.txt'
yuanyin_output_file = 'yuanyin_output.txt'

line_arr = []
input_file = open(benefit_title_file)
for line in input_file.readlines():
    line = line.strip().decode('utf-8')
    line_info = line.split('|')
    if len(line_info) < 4:
        continue
    line_arr.append([int(line_info[0]), line_info[1], int(line_info[2])])
input_file.close()

input_file = open(yuanyin_output_file)
line_count = 0
last_pid = -1
reset_yuanyin_flag = False
for line in input_file.readlines():
    line = line.strip().decode('utf-8')
    line_info = line.split('|')
    if len(line_info) < 3:
        continue
    line_arr_obj = line_arr[line_count]

    if line_arr_obj[0] != last_pid:
        reset_yuanyin_flag = False
    if line_arr_obj[2] != 0:
        reset_yuanyin_flag = False

    if line_arr_obj[2] == 1 and line_arr_obj[1].find(u'意外') != -1:
        reset_yuanyin_flag = True

    yuanyin_label = int(line_info[2])
    if reset_yuanyin_flag == True and yuanyin_label != 0:
        # if yuanyin_label != 1:
        #     print line_count
        line_arr_obj.append(1)
    else:
        line_arr_obj.append(int(yuanyin_label))
    line_arr[line_count] = line_arr_obj

    last_pid = line_arr_obj[0]
    line_count += 1
input_file.close()

output_file = open('yuanyin_output_tmp.txt', 'w')
# output_file = open(yuanyin_output_file, 'w') 
for obj in line_arr:
    str_tmp = '%s|%s|%s\n' % (obj[0], obj[1], obj[3])
    output_file.write(str_tmp.encode('utf-8'))
output_file.close()

