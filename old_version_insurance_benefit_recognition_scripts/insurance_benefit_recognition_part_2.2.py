# -*- coding: utf-8 -*-

import re

print '本程序还在测试版，将疾病保险金提取出来做框架分析，目前输入为benefit_title_output_with_dengdaiqi_yuanyin。分析维度包括：等待期、事故原因'

def two_arr_permutation_and_combination(a, b):
    ret = []
    if len(a) > 0:
        for i in a:
            if len(b) > 0:
                for j in b:
                    ret.append(i+'+'+j)
            else:
                ret.append(i)
    else:
        if len(b) > 0:
            for j in b:
                ret.append(j)
        else:
            pass
    return ret
    
def arrs_permutation_and_combination(*args):
    ret = []
    for set_tmp in args:
        ret = two_arr_permutation_and_combination(ret, set_tmp)
    return ret

def condition_combination(line_arr):
    dengdaiqi_status_arr = []
    yuanyin_status_arr = []

    for obj in line_arr:
        sentence_tmp = obj[0]
        is_dengdaiqi_tmp = obj[2]
        is_yuanyin_tmp = obj[3]

        dengdaiqi_found_flag = False
        dengdaiqi_dict = {
            '1': [u'等待期内'],
            '2': [u'等待期外'],
            '3': [u'等待期内', u'等待期外'],
        }
        if is_dengdaiqi_tmp > 0:
        # 等待期判断
            match1 = re.search(ur'等待期.{0,5}[内]', sentence_tmp)
            match2 = re.search(ur'合同生效.*起.*[前|内]', sentence_tmp)
            if match1 or match2:
                dengdaiqi_status_arr.append(u'等待期内')
                dengdaiqi_found_flag = True

            match1 = re.search(ur'等待期.{0,5}[外后]+', sentence_tmp)
            match2 = re.search(ur'合同生效.*起.*[后外]', sentence_tmp)
            if match1 or match2:
                dengdaiqi_status_arr.append(u'等待期外')
                dengdaiqi_found_flag = True

            match1 = re.search(ur'不受.*限制', sentence_tmp)
            match2 = re.search(ur'无等待期', sentence_tmp)
            if match1 or match2:
                dengdaiqi_status_arr.append(u'等待期内')
                dengdaiqi_status_arr.append(u'等待期外')
                dengdaiqi_found_flag = True

            if dengdaiqi_found_flag == False:
                dengdaiqi_status_arr.extend(dengdaiqi_dict[str(is_dengdaiqi_tmp)])
                dengdaiqi_found_flag = True

        yuanyin_found_flag = False
        yuanyin_dict = {
            '1': [u'意外'],
            '2': [u'非意外'],
            '3': [u'意外', u'非意外'],
        }
        # 事故原因判断
        match1 = re.search(ur'[因遭受]+.{0,4}意外[伤害事故]+', sentence_tmp)
	if match1:
            pos_tmp = sentence_tmp.find(match1.group(0))
            sentence_tmp_former_part = sentence_tmp[0:pos_tmp]
            sentence_tmp_latter_part = sentence_tmp[pos_tmp+len(match1.group(0)):pos_tmp+len(match1.group(0))+10]
            if sentence_tmp_former_part.find(u'非') == -1 and sentence_tmp_latter_part.find(u'以外') == -1:
                yuanyin_status_arr.append(u'意外')
                print (u'%s|%s'%(sentence_tmp,1)).encode('utf-8')

        match1 = re.search(ur'非.{0,10}[因遭受]+.{0,4}意外[伤害事故]+', sentence_tmp)
        if match1:
            yuanyin_status_arr.append(u'非意外')
            print (u'%s|%s'%(sentence_tmp,2)).encode('utf-8')

        match1 = re.search(ur'[因遭受]+.{0,4}意外[伤害事故]+.{0,10}以外', sentence_tmp)
        if match1:
            yuanyin_status_arr.append(u'非意外')
            print (u'%s|%s'%(sentence_tmp,3)).encode('utf-8')

        match1 = re.search(ur'突发', sentence_tmp)
        if match1:
            yuanyin_status_arr.append(u'意外')
            print (u'%s|%s'%(sentence_tmp,4)).encode('utf-8')

        match1 = re.search(ur'因.{0,5}疾病', sentence_tmp)
        if match1:
            yuanyin_status_arr.append(u'非意外')
            print (u'%s|%s'%(sentence_tmp,5)).encode('utf-8')

        match1 = re.search(ur'疾病.{0,5}导致', sentence_tmp)
        if match1:
            yuanyin_status_arr.append(u'非意外')
            print (u'%s|%s'%(sentence_tmp,6)).encode('utf-8')

    dengdaiqi_status_arr = list(set(dengdaiqi_status_arr))
    yuanyin_status_arr = list(set(yuanyin_status_arr))
    dengdaiqi_status_arr.sort()
    yuanyin_status_arr.sort()

    return arrs_permutation_and_combination(dengdaiqi_status_arr, yuanyin_status_arr)

# input_file = open('benefit_title_output_with_dengdaiqi_yuanyin')
input_file = open('/home/ck/sentence_splitting/output.txt')
benefit_line_arr = []
last_pid = -1
pid_arr = []
# print u'产品PID|保险金名称|等待期内|等待期外|意外|非意外'.encode('utf-8')
for line in input_file.readlines():
    line = line.strip().decode('utf-8')
    line_info = line.split('|')

    if len(line_info) < 5:
        continue

    if line_info[0].isdigit() == False:
        continue

    pid = int(line_info[0])
    sentence = line_info[1]
    is_title = int(line_info[2])
    is_dengdaiqi = int(line_info[3])
    is_yuanyin = int(line_info[4])
    # 1 医疗费用
    # 2 重大疾病
    # 3 理财储蓄
    # 4 人寿意外
    # benefit_type = int(line_info[3])

    if pid != 16909:
        continue

    flush_flag = False

    if pid != last_pid:
        pid_arr.append(pid)
        
    if pid != last_pid and last_pid != -1 and len(benefit_line_arr) > 0:
        flush_flag = True

    if is_title == 1 and len(benefit_line_arr) > 0:
        flush_flag = True

    if flush_flag == True:
        # TODO output condition combination and initialize benefit_line_arr
        if benefit_line_arr[0][1] == 1:
            benefit_title = benefit_line_arr[0][0]
            ret = condition_combination(benefit_line_arr)
            if len(ret) > 0:
               for i in ret:
                  param1, param2, param3, param4 = 0, 0, 0, 0
                  if i.find(u'等待期内') != -1:
                      param1 = 1
                      param2 = 0
                  if i.find(u'等待期外') != -1:
                      param1 = 0
                      param2 = 1
                  if i.find(u'意外') != -1 and i.find(u'非意外') == -1:
                      param3 = 1
                      param4 = 0
                  if i.find(u'非意外') != -1:
                      param3 = 0
                      param4 = 1
                  # print (u'%s|%s|%s|%s|%s|%s'%(last_pid, benefit_title, param1, param2, param3, param4)).encode('utf-8')
                  # print (u'%s|%s|%s'%(last_pid, benefit_title,i)).encode('utf-8')
            else:
                # print (u'%s|%s|%s|%s|%s|%s'%(last_pid, benefit_title, 0, 0, 0, 0)).encode('utf-8')
                # print (u'%s|%s|%s'%(last_pid, benefit_title,u'无条件')).encode('utf-8')
                pass
        benefit_line_arr = []

    benefit_line_arr.append((sentence, is_title, is_dengdaiqi, is_yuanyin))
    last_pid = pid

input_file.close()

if len(benefit_line_arr) > 0:
    if benefit_line_arr[0][1] == 1:
        benefit_title = benefit_line_arr[0][0]
        ret = condition_combination(benefit_line_arr)
        if len(ret) > 0:
            for i in ret:
               param1, param2, param3, param4 = 0, 0, 0, 0
               if i.find(u'等待期内') != -1:
                   param1 = 1
                   param2 = 0
               if i.find(u'等待期外') != -1:
                   param1 = 0
                   param2 = 1
               if i.find(u'意外') != -1 and i.find(u'非意外') == -1:
                   param3 = 1
                   param4 = 0
               if i.find(u'非意外') != -1:
                   param3 = 0
                   param4 = 1
               # print (u'%s|%s|%s|%s|%s|%s'%(last_pid, benefit_title, param1, param2, param3, param4)).encode('utf-8')
               # print (u'%s|%s|%s'%(last_pid, benefit_title,i)).encode('utf-8')
        else:
            # print (u'%s|%s|%s|%s|%s|%s'%(last_pid, benefit_title, 0, 0, 0, 0)).encode('utf-8')
            # print (u'%s|%s|%s'%(last_pid, benefit_title,u'无条件')).encode('utf-8')
            pass
    benefit_line_arr = []

# print pid_arr
