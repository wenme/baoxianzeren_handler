# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import re
import datetime 

input_file_name = 'aggregation_label_table.txt'
output_file_name = 'aggregation_payment_combos.txt'
print '本程序提取2.4的输出文件aggregation_label_table.txt中各个保险金的给付条件，并根据各个条件的排列组合生成给付情形'
print '输出给付情况组合：%s' % output_file_name

def two_arr_permutation_and_combination(a, b):
    ret = []
    if len(a) > 0:
        for i in a:
            if len(b) > 0:
                for j in b:
                    ret.append('%s|%s'%(str(i),str(j)))
            else:
                ret.append('%s'%(str(i)))
    else:
        if len(b) > 0:
            for j in b:
                ret.append('%s'%(str(j)))
        else:
            pass
    return ret

def arrs_permutation_and_combination(*args):
    ret = []
    for i in args:
        ret = two_arr_permutation_and_combination(ret, i)
    return ret

def fix_dengdaiqi(dengdaiqi, sentence_tmp):
    # 1-等待期内
    # 2-等待期外
    # 3-不受等待期限制
    # if is_dengdaiqi > 0:
    #     # 等待期判断
    #     match1 = re.search(ur'等待期.{0,5}[内]', sentence_tmp)
    #     match2 = re.search(ur'合同生效.*起.*[前|内]', sentence_tmp)
    #     if match1 or match2:
    #         return 1

    #     match1 = re.search(ur'等待期.{0,5}[外后]+', sentence_tmp)
    #     match2 = re.search(ur'合同生效.*起.*[后外]', sentence_tmp)
    #     if match1 or match2:
    #         return 2

    #     match1 = re.search(ur'不受.*限制', sentence_tmp)
    #     match2 = re.search(ur'无等待期', sentence_tmp)
    #     if match1 or match2:
    #         return 3
    # if dengdaiqi == 3:
    #     return [1, 2]
    # elif dengdaiqi > 0 and dengdaiqi < 3:
    #     return [dengdaiqi]
    # else:
    #     return []
    if dengdaiqi > 0:
        return [1,2]
    else:
          return []

def fix_yuanyin(yuanyin, sentence_tmp):
    # 1-意外
    # 2-非意外
    # 3-意外&非意外
    # yiwai_flag = False
    # feiyiwai_flag = False

    # # 事故原因判断
    # match1 = re.search(ur'[因遭受]+.{0,4}意外[伤害事故]+', sentence_tmp)
    # if match1:
    #     pos_tmp = sentence_tmp.find(match1.group(0))
    #     sentence_tmp_former_part = sentence_tmp[0:pos_tmp]
    #     sentence_tmp_latter_part = sentence_tmp[pos_tmp+len(match1.group(0)):pos_tmp+len(match1.group(0))+10]
    #     if sentence_tmp_former_part.find(u'非') == -1 and sentence_tmp_latter_part.find(u'以外') == -1:
    #         yiwai_flag= True
    #         # print (u'%s|%s'%(sentence_tmp,1)).encode('utf-8')

    # match1 = re.search(ur'非.{0,10}[因遭受]+.{0,4}意外[伤害事故]+', sentence_tmp)
    # if match1:
    #     feiyiwai_flag = True
    #     # print (u'%s|%s'%(sentence_tmp,2)).encode('utf-8')

    # match1 = re.search(ur'[因遭受]+.{0,4}意外[伤害事故]+.{0,10}以外', sentence_tmp)
    # if match1:
    #     feiyiwai_flag = True
    #     # print (u'%s|%s'%(sentence_tmp,3)).encode('utf-8')

    # match1 = re.search(ur'突发', sentence_tmp)
    # if match1:
    #     yiwai_flag= True
    #     # print (u'%s|%s'%(sentence_tmp,4)).encode('utf-8')

    # match1 = re.search(ur'因.{0,5}疾病', sentence_tmp)
    # if match1:
    #     feiyiwai_flag = True
    #     # print (u'%s|%s'%(sentence_tmp,5)).encode('utf-8')

    # match1 = re.search(ur'疾病.{0,5}导致', sentence_tmp)
    # if match1:
    #     feiyiwai_flag = True
    #     # print (u'%s|%s'%(sentence_tmp,6)).encode('utf-8')

    # if yiwai_flag and feiyiwai_flag:
    #     return [1, 2]
    # elif yiwai_flag:
    #     return [1]
    # elif feiyiwai_flag:
    #     return [2]
    # else:
    #     if yuanyin == 3:
    #         return [1, 2]
    #     elif yuanyin > 0 and yuanyin < 3:
    #         return [yuanyin]
    #     else:
    #         return []
    # if sentence_tmp.find(u'意外') != -1:
    #     return [1]
    # else:
    #     return [yuanyin]
    if yuanyin > 0:
        return [1,2]
    else:
        return []

def fix_beibaorennianling(beibaorennianling, sentence_tmp):
    # beibaorennianling_dict = {
    #     '1': [u'前'],
    #     '2': [u'后'],
    #     '3': [u'之间'],
    #     '4': [u'至']
    # }
    if beibaorennianling > 0:
        return [beibaorennianling]
    else:
        return []

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
        kw = [u'投资单位价值总额',u'投资账户',u'账户价值',u'账户余额']
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
        if match1:
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
        ret.sort()
        return ret

    else:
        return []

benefit_payment_combo_table = []
last_pid = -1
flush = False
foreline_end = False
foreline_arr = []
benefit_line_arr = []

input_file = open(input_file_name)
line_count = 0
time1 = datetime.datetime.now()
print 'start generating...', time1
for line in input_file.readlines():
    line = line.strip().decode('utf-8')
    line_info = line.split('|')
    line_count += 1

    if len(line_info) < 7:
        continue

    pid = int(line_info[0])
    sentence = line_info[1]
    is_title = int(line_info[2])
    dengdaiqi = int(line_info[3])
    yuanyin = int(line_info[4])
    beibaorennianling = int(line_info[5])
    jifujine = int(line_info[6])

    if pid != last_pid:
        foreline_end = False
        # print 1, sentence
    if is_title == 1 and foreline_end == True:
        flush = True
        # print 2, sentence
    if is_title == 1 and foreline_end == False:
        foreline_end = True
        # print 3, sentence
    if pid != last_pid and last_pid != -1:
        flush = True
        # print 4, sentence
    if flush:
        # TODO flush things
        # print pid, sentence
        line_arr_tmp = []
        line_arr_tmp.extend(foreline_arr)
        line_arr_tmp.extend(benefit_line_arr)
        if len(benefit_line_arr) > 0:
            benefit_name = benefit_line_arr[0][0]
        else:
            benefit_name = u'默认保险金标题'
        dengdaiqi_arr = []
        yuanyin_arr = []
        beibaorennianling_arr = []
        jifujine_arr = []
        benefit_str = u''
        for line_obj in line_arr_tmp:
            # print 'dengdaiqi:', line_obj[1], fix_dengdaiqi(line_obj[1], line_obj[0]), line_obj[0]
            # print 'yuanyin:', line_obj[2], fix_yuanyin(line_obj[2], line_obj[0]), line_obj[0]
            # print 'beibaorennianling:', line_obj[3], fix_beibaorennianling(line_obj[3], line_obj[0]), line_obj[0]
            # print 'jifujine:', line_obj[4], fix_jifujine(line_obj[4], line_obj[0]), line_obj[0]
            dengdaiqi_arr.extend(fix_dengdaiqi(line_obj[1], line_obj[0]))
            yuanyin_arr.extend(fix_yuanyin(line_obj[2], benefit_name))
            beibaorennianling_arr.extend(fix_beibaorennianling(line_obj[3], line_obj[0]))
            jifujine_arr.extend(fix_jifujine(line_obj[4], line_obj[0]))
            benefit_str += line_obj[0]

        dengdaiqi_arr = list(set(dengdaiqi_arr))
        if len(dengdaiqi_arr) > 0:
            dengdaiqi_arr.sort()
        else:
            dengdaiqi_arr.append(0)

        yuanyin_arr = list(set(yuanyin_arr))
        if len(yuanyin_arr) > 0:
            yuanyin_arr.sort()
        else:
            yuanyin_arr.append(0)

        beibaorennianling_arr = list(set(beibaorennianling_arr))
        if len(beibaorennianling_arr) > 0:
            beibaorennianling_arr.sort()
        else:
            beibaorennianling_arr.append(0)

        jifujine_arr = list(set(jifujine_arr))
        if len(jifujine_arr) > 0:
            jifujine_arr.sort()
        else:
            jifujine_arr.append(0)

        # print dengdaiqi_arr
        # print yuanyin_arr
        # print beibaorennianling_arr
        # print jifujine_arr
        # print '%s\t%s\t%s' % (last_pid, benefit_name, str([len(dengdaiqi_arr), len(yuanyin_arr), len(beibaorennianling_arr), len(jifujine_arr)]))
        ret_combos = arrs_permutation_and_combination(dengdaiqi_arr, yuanyin_arr, beibaorennianling_arr, jifujine_arr)
        for combo in ret_combos:
            str_tmp = '%s|%s|%s|%s\n' % (last_pid, benefit_name, combo, benefit_str)
            benefit_payment_combo_table.append(str_tmp)

        benefit_line_arr = []
        flush = False

    if pid != last_pid:
        foreline_arr = []

    if foreline_end == False:
        foreline_arr.append((sentence, dengdaiqi, yuanyin, beibaorennianling, jifujine))
    else:
        benefit_line_arr.append((sentence, dengdaiqi, yuanyin, beibaorennianling, jifujine))

    last_pid = pid

    # if line_count > 659:
    #     break

    if line_count % 1000 == 0:
        print line_count

# push content that left in the buffer
if len(benefit_line_arr) > 0:
    # TODO flush things
    line_arr_tmp = []
    line_arr_tmp.extend(foreline_arr)
    line_arr_tmp.extend(benefit_line_arr)
    benefit_name = benefit_line_arr[0][0]
    dengdaiqi_arr = []
    yuanyin_arr = []
    beibaorennianling_arr = []
    jifujine_arr = []
    benefit_str = u''
    for line_obj in line_arr_tmp:
        # print 'dengdaiqi:', line_obj[1], fix_dengdaiqi(line_obj[1], line_obj[0]), line_obj[0]
        # print 'yuanyin:', line_obj[2], fix_yuanyin(line_obj[2], line_obj[0]), line_obj[0]
        # print 'beibaorennianling:', line_obj[3], fix_beibaorennianling(line_obj[3], line_obj[0]), line_obj[0]
        # print 'jifujine:', line_obj[4], fix_jifujine(line_obj[4], line_obj[0]), line_obj[0]
        dengdaiqi_arr.extend(fix_dengdaiqi(line_obj[1], line_obj[0]))
        yuanyin_arr.extend(fix_yuanyin(line_obj[2], line_obj[0]))
        beibaorennianling_arr.extend(fix_beibaorennianling(line_obj[3], line_obj[0]))
        jifujine_arr.extend(fix_jifujine(line_obj[4], line_obj[0]))
        benefit_str += line_obj[0]

    dengdaiqi_arr = list(set(dengdaiqi_arr))
    if len(dengdaiqi_arr) > 0:
        dengdaiqi_arr.sort()
    else:
        dengdaiqi_arr.append(0)

    yuanyin_arr = list(set(yuanyin_arr))
    if len(yuanyin_arr) > 0:
        yuanyin_arr.sort()
    else:
        yuanyin_arr.append(0)

    beibaorennianling_arr = list(set(beibaorennianling_arr))
    if len(beibaorennianling_arr) > 0:
        beibaorennianling_arr.sort()
    else:
        beibaorennianling_arr.append(0)

    jifujine_arr = list(set(jifujine_arr))
    if len(jifujine_arr) > 0:
        jifujine_arr.sort()
    else:
        jifujine_arr.append(0)

    # print '%s\t%s' % (benefit_name, str([len(dengdaiqi_arr), len(yuanyin_arr), len(beibaorennianling_arr), len(jifujine_arr)]))
    ret_combos = arrs_permutation_and_combination(dengdaiqi_arr, yuanyin_arr, beibaorennianling_arr, jifujine_arr)
    for combo in ret_combos:
        str_tmp = '%s|%s|%s|%s\n' % (last_pid, benefit_name, combo, benefit_str)
        benefit_payment_combo_table.append(str_tmp)

input_file.close()

output_file = open(output_file_name, 'w')
for line in benefit_payment_combo_table:
    output_file.write(line.encode('utf-8'))
output_file.close()
time2 = datetime.datetime.now()
print 'Done!', time2
print 'it took %s seconds~' % (time2-time1)
