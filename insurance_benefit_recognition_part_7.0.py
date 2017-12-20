# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import re
import datetime 

output_file_aggragation_table = 'aggregation_label_table.txt'
print '本程序按顺序将之前的输出文件benefit_title_output_splitted.txt, dengdaiqi_output.txt, yuanyin_output.txt, beibaorennianling_output.txt, baodanniandu_output.txt, jifujine_output.txt合并成一个文件'
print '输出文件聚合表格：%s' % output_file_aggragation_table
file_list = ['./test_data_set/benefit_title_output_splitted.txt', 'dengdaiqi_output.txt', 'yuanyin_output.txt', 'beibaorennianling_output.txt', 'baodanniandu_output.txt', 'jifujine_output.txt']

time1 = datetime.datetime.now()
print 'start merging...', time1
df = pd.DataFrame()
for file_obj in file_list:
    pid_arr = []
    sentence_arr = []
    label_arr = []
    value_arr = []
    with open(file_obj) as file_tmp:
        for line in file_tmp.readlines():
            line = line.strip().decode('utf-8')
            line_info = line.split('|')
            pid_arr.append(int(line_info[0]))
            sentence_arr.append(line_info[1])
            label_arr.append(line_info[2])
            value_arr.append(line_info[3])
    if file_obj.find('benefit_title_output_splitted') != -1:
        df['pid'] = np.asarray(pid_arr)
        df['sentence'] = np.asarray(sentence_arr)
        df['is_title'] = np.asarray(label_arr)
        df['benefit_type'] = np.asarray(value_arr)
    elif file_obj.find('dengdaiqi') != -1:
        # df['pid_2'] = np.asarray(pid_arr)
        # df['sentence_2'] = np.asarray(sentence_arr)
        df['dengdaiqi'] = np.asarray(label_arr)
        df['dengdaiqi_value'] = np.asarray(value_arr)
    elif file_obj.find('yuanyin') != -1:
        # df['pid_3'] = np.asarray(pid_arr)
        # df['sentence_3'] = np.asarray(sentence_arr)
        df['yuanyin'] = np.asarray(label_arr)
        df['yuanyin_value'] = np.asarray(value_arr)
    elif file_obj.find('beibaorennianling') != -1:
        # df['pid_4'] = np.asarray(pid_arr)
        # df['sentence_4'] = np.asarray(sentence_arr)
        df['beibaorennianling'] = np.asarray(label_arr)
        df['beibaorennianling_value'] = np.asarray(value_arr)
    elif file_obj.find('baodanniandu') != -1:
        # df['pid_5'] = np.asarray(pid_arr)
        # df['sentence_5'] = np.asarray(sentence_arr)
        df['baodanniandu'] = np.asarray(label_arr)
        df['baodanniandu_value'] = np.asarray(value_arr)
    elif file_obj.find('jifujine') != -1:
        # df['pid_6'] = np.asarray(pid_arr)
        # df['sentence_6'] = np.asarray(sentence_arr)
        df['jifujine'] = np.asarray(label_arr)
        df['jifujine_value'] = np.asarray(value_arr)
    else:
        print 'file name error! please add new file obj here!'
        exit()

output_file = open(output_file_aggragation_table, 'w')
str_tmp = u'pid|sentence|is_title|benefit_type|dengdaiqi|dengdaiqi_value|yuanyin|yuanyin_value|beibaorennianling|beibaorannianling_value|baodanniandu|baodanniandu_value|jifujine|jifujine_value\n'
output_file.write(str_tmp.encode('utf-8'))
for i in range(0, len(df)):
    pid = df['pid'][i]
    sentence = df['sentence'][i]
    is_title = df['is_title'][i]
    benefit_type = df['benefit_type'][i]
    dengdaiqi = df['dengdaiqi'][i]
    dengdaiqi_value = df['dengdaiqi_value'][i]
    yuanyin = df['yuanyin'][i]
    yuanyin_value = df['yuanyin_value'][i]
    beibaorennianling = df['beibaorennianling'][i]
    beibaorennianling_value = df['beibaorennianling_value'][i]
    baodanniandu = df['baodanniandu'][i]
    baodanniandu_value = df['baodanniandu_value'][i]
    jifujine = df['jifujine'][i]
    jifujine_value = df['jifujine_value'][i]
    str_tmp = u'%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (pid, sentence, is_title, benefit_type, dengdaiqi, dengdaiqi_value, yuanyin, yuanyin_value, beibaorennianling, beibaorennianling_value, baodanniandu, baodanniandu_value, jifujine, jifujine_value)
    output_file.write(str_tmp.encode('utf-8'))
output_file.close()
time2 = datetime.datetime.now()
print 'done!', time2
print 'It took %s seconds' % (time2-time1)
