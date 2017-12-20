# -*- coding: utf-8 -*-

from sys import argv
import re
import random

output_file_path = 'benefit_payments.txt'
print '本程序用于根据上一步骤输出的文件aggregation_label_table_tmp.txt或aggregation_label_table.txt生成给付情形'
print '输入参数一：aggregation_label_table_tmp.txt'
print '输出：%s' % output_file_path

def two_arr_permutation_and_combination(a, b):
    ret = []
    if len(a) > 0:
        for i in a:
            if len(b) > 0:
                for j in b:
                    ret.append(u'%s|%s'%(i,j))
            else:
                ret.append(u'%s'%(i))
    else:
        if len(b) > 0:
            for j in b:
                ret.append(u'%s'%(j))
        else:
            pass
    return ret

def arrs_permutation_and_combination(*args):
    ret = []
    for i in args:
        ret = two_arr_permutation_and_combination(ret, i)
    return ret

def fix_dengdaiqi(dengdaiqi, sentence_tmp):
    if dengdaiqi > 0:
        return [1,2]
    else:
          return []

def fix_yuanyin(yuanyin, sentence_tmp):
    if yuanyin > 0:
        return [1,2]
    else:
        return []

def fix_beibaorennianling(beibaorennianling, sentence_tmp):
    if beibaorennianling > 0:
        return [beibaorennianling]
    else:
        return []

def fix_jifujine(jifujine, sentence_tmp):
    # 1 保险金额
    # 5 豁免
    # 6 实际费用  补贴额  具体金额  约定金额
    # 以上三种归为保险公司承担责任的jifujine即为1，其余为2
    if jifujine != '0':
        if jifujine.find('1') != -1 or jifujine.find('5') != -1 or jifujine.find('6') != -1:
            return [1]
        else:
            return [2]
    else:
        return []

def analyze_benefit_payments_special(benefit_line_arr, dengdaiqi_line_arr):
    dengdaiqi_dict = {
        '0': u'无',
        '1': u'等待期内',
        '2': u'等待期外',
        '3': u'等待期内及等待期外'
    }
    yuanyin_dict = {
        '0': u'无',
        '1': u'意外',
        '2': u'非意外',
        '3': u'意外及非意外'
    }
    beibaorennianling_dict = {
        '0': u'无',
        '1': u'之前',
        '2': u'之后',
        '3': u'之间',
        '4': u'至'
    }
    jifujine_dict = {
        '-1': u'无匹配金额',
        '0': u'无',
        '1': u'保额',
        '2': u'保险费',
        '3': u'账户价值',
        '4': u'现金价值',
        '5': u'豁免',
        '6': u'其他',
    }
    def jifujine_translator(jifujine_str):
        ret = []
        for i in jifujine_str.split('+'):
            ret.append(jifujine_dict[i])
        if len(ret) > 1:
            return '(' + '+'.join(ret) + ')'
        elif len(ret) == 1:
            return ret[0]
        else:
            return u'无金额'

    benefit_payments_combo_table = []
    line_arr_tmp = []
    line_arr_tmp.extend(dengdaiqi_line_arr)
    line_arr_tmp.extend(benefit_line_arr)

    benefit_name = u'默认保险金标题'

    dengdaiqi_arr = []
    yuanyin_arr = []
    beibaorennianling_arr = []
    beibaorennianling_value_json = {}
    jifujine_arr = []
    jifujine_original_arr = []
    benefit_str = u''

    before_18_flag = False
    benefit_type_4_flag = False
    benefit_consequence = -1
    jifujine_relation = 0
    jifujine_str_buf = u'' # store plain-text jifujine
    jifujine_buf = u'' # store numerical jifujine
    for line in line_arr_tmp:
        line_info = line.split('|')
        pid = int(line_info[0])
        sentence = line_info[1]
        is_title = int(line_info[2])
        consequence = int(line_info[3])
        dengdaiqi = int(line_info[4])
        dengdaiqi_value = line_info[5].strip()
        yuanyin = int(line_info[6])
        yuanyin_value = line_info[7].strip()
        beibaorennianling = int(line_info[8])
        beibaorennianling_value = line_info[9].strip()
        baodanniandu = int(line_info[10])
        baodanniandu_value = line_info[11].strip()
        jifujine = line_info[12]
        jifujine_value = line_info[13].strip()
        relation = int(line_info[14])

        if is_title == 1:
            benefit_name = sentence
            benefit_consequence = consequence
            if consequence == 4:
                benefit_type_4_flag = True

        if beibaorennianling == 1 and beibaorennianling_value.find('18') != -1:
            before_18_flag = True

        if beibaorennianling != 0:
            beibaorennianling_value_json[str(beibaorennianling)] = beibaorennianling_value

        if relation != 0:
            jifujine_relation = relation

        if jifujine != '0' or jifujine.find(u'+') != -1:
            if jifujine_value != '':
                jifujine_str_tmp = u'%sx%s' % (jifujine_translator(jifujine), jifujine_value)
            else:
                jifujine_str_tmp = u'%s' % (jifujine_translator(jifujine))

            if jifujine_relation == 0:
                # if no relation exists, append jifujine_buf directly
                jifujine_buf = jifujine

                if jifujine_buf.find(u'1') != -1 or jifujine_buf.find(u'5') != -1 or jifujine_buf.find(u'6') != -1:
                    jifujine_original_arr.append((jifujine_str_tmp,1))
                else:
                    jifujine_original_arr.append((jifujine_str_tmp,2))
                jifujine_arr.extend(fix_jifujine(jifujine_buf, sentence))
                jifujine_buf = u''
                jifujine_str_buf = u''

            elif jifujine_relation == 1:
                if jifujine_buf == u'':
                    jifujine_buf = u'MAX( %s,' % jifujine
                else:
                    jifujine_buf += u'%s )' % jifujine
                    jifujine_arr.extend(fix_jifujine(jifujine_buf, sentence))

                if jifujine_str_buf == u'':
                    jifujine_str_buf = u'MAX( %s,' % jifujine_str_tmp
                else:
                    jifujine_str_buf += u'%s )'  % jifujine_str_tmp
                    if jifujine_buf.find(u'1') != -1 or jifujine_buf.find(u'5') != -1 or jifujine_buf.find(u'6') != -1:
                        jifujine_original_arr.append((jifujine_str_buf,1))
                    else:
                        jifujine_original_arr.append((jifujine_str_tmp,2))
                    jifujine_buf = u''
                    jifujine_str_buf = u''
                    jifujine_relation = 0

            else:
                if jifujine_buf == u'':
                    jifujine_buf = u'SUM( %s,' % jifujine
                else:
                    jifujine_buf += u'%s )' % jifujine
                    jifujine_arr.extend(fix_jifujine(jifujine_buf, sentence))

                if jifujine_str_buf == u'':
                    jifujine_str_buf = u'SUM( %s,' % jifujine_str_tmp
                else:
                    jifujine_str_buf += u'%s )'  % jifujine_str_tmp
                    if jifujine_buf.find(u'1') != -1 or jifujine_buf.find(u'5') != -1 or jifujine_buf.find(u'6') != -1:
                        jifujine_original_arr.append((jifujine_str_buf,1))
                    else:
                        jifujine_original_arr.append((jifujine_str_tmp,2))
                    jifujine_buf = u''
                    jifujine_str_buf = u''
                    jifujine_relation = 0

        dengdaiqi_arr.extend(fix_dengdaiqi(dengdaiqi, sentence))
        yuanyin_arr.extend(fix_yuanyin(yuanyin, sentence))
        beibaorennianling_arr.extend(fix_beibaorennianling(beibaorennianling, sentence))
        benefit_str += sentence

    dengdaiqi_arr = list(set(dengdaiqi_arr))
    if len(dengdaiqi_arr) > 0:
        dengdaiqi_arr.sort()
    else:
        dengdaiqi_arr.append(0)

    yuanyin_arr = list(set(yuanyin_arr))
    if benefit_name.find(u'非意外') == -1 and benefit_name.find(u'意外全残') != -1 and (2 in yuanyin_arr):
        yuanyin_arr.remove(2)
    if benefit_name.find(u'非意外') == -1 and benefit_name.find(u'意外身故') != -1 and (2 in yuanyin_arr):
        yuanyin_arr.remove(2)
    if benefit_name.find(u'非疾病') == -1 and benefit_name.find(u'疾病全残') != -1 and (1 in yuanyin_arr):
        yuanyin_arr.remove(1)
    if benefit_name.find(u'非疾病') == -1 and benefit_name.find(u'疾病身故') != -1 and (1 in yuanyin_arr):
        yuanyin_arr.remove(1)
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
    jifujine_original_arr = list(set(jifujine_original_arr))

    ret_combos = arrs_permutation_and_combination(dengdaiqi_arr, yuanyin_arr, beibaorennianling_arr, jifujine_arr)
    payment_count = 1
    for combo in ret_combos:
        info_arr = combo.split('|')
        payment_reasonable_flag = False
        # if beibaorennianling is before 18 and benefit type is 4, follows the rules below
        if benefit_type_4_flag and before_18_flag and info_arr[2] == '1' and info_arr[3] == '1':
            payment_reasonable_flag = False
        elif benefit_type_4_flag and before_18_flag and info_arr[2] == '1' and info_arr[3] == '2':
            payment_reasonable_flag = True
        elif info_arr[0] == '2' and info_arr[3] == '1':
            payment_reasonable_flag = True
        elif info_arr[0] == '1' and info_arr[1] == '1' and info_arr[3] == '1':
            payment_reasonable_flag = True
        elif info_arr[0] == '1' and info_arr[1] == '2' and info_arr[3] == '2':
            payment_reasonable_flag = True
        else:
            payment_reasonable_flag = False

        if payment_reasonable_flag == False:
            continue

        beibaorennianling_str_tmp = u'无'
        if info_arr[2] != '0':
            beibaorennianling_str_tmp = u'%s %s' % (beibaorennianling_value_json[info_arr[2]], beibaorennianling_dict[info_arr[2]])
        jifujine_str_tmp = u''
        if info_arr[3] == '1':
            for jifujine_obj_tmp in jifujine_original_arr:
                if jifujine_obj_tmp[1] == 1:
                    jifujine_str_tmp += jifujine_obj_tmp[0] + ','
        else:
            for jifujine_obj_tmp in jifujine_original_arr:
                if jifujine_obj_tmp[1] == 2:
                    jifujine_str_tmp += jifujine_obj_tmp[0] + ','
        if jifujine_str_tmp.rfind(',') == len(jifujine_str_tmp) - 1:
            jifujine_str_tmp = jifujine_str_tmp[0:len(jifujine_str_tmp)-1]

        str_tmp = u'%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (last_pid, benefit_name, benefit_consequence, payment_count, dengdaiqi_dict[info_arr[0]], yuanyin_dict[info_arr[1]], beibaorennianling_str_tmp, u'无', jifujine_str_tmp.strip(), benefit_str)
        benefit_payments_combo_table.append(str_tmp)
        payment_count += 1

    return benefit_payments_combo_table
    
def analyze_benefit_payments_regular(benefit_line_arr):
    consequence_dict = {
        '0': u'其他',
        '1': u'医疗费用',
        '2': u'重大疾病',
        '3': u'理财储蓄',
        '4': u'人寿意外'
    }
    dengdaiqi_dict = {
        '0': u'无',
        '1': u'等待期内',
        '2': u'等待期外',
        '3': u'等待期内及等待期外'
    }
    yuanyin_dict = {
        '0': u'无',
        '1': u'意外',
        '2': u'非意外',
        '3': u'意外及非意外'
    }
    beibaorennianling_dict = {
        '0': u'无',
        '1': u'之前',
        '2': u'之后',
        '3': u'之间',
        '4': u'至'
    }
    baodanniandu_dict = {
        '0': u'无',
        '1': u'之前',
        '2': u'之后',
        '3': u'之间',
        '4': u'至'
    }
    jifujine_dict = {
        '-1': u'无匹配金额',
        '0': u'无',
        '1': u'保额',
        '2': u'保险费',
        '3': u'账户价值',
        '4': u'现金价值',
        '5': u'豁免',
        '6': u'其他',
    }
    def jifujine_translator(jifujine_str):
        ret = []
        for i in jifujine_str.split('+'):
            ret.append(jifujine_dict[i])
        if len(ret) > 1:
            return '(' + '+'.join(ret) + ')'
        elif len(ret) == 1:
            return ret[0]
        else:
            return u'无金额'

    benefit_payments_combo_table = []
    benefit_name = u'默认保险金'
    benefit_consequence = -1
    dengdaiqi_str = u''
    yuanyin_str = u''
    beibaorennianling_str = u''
    baodanniandu_str = u''
    jifujine_str = u''
    jifujine_relation = 0
    end_of_benefit_payment = False
    waiting_for_first_period = False
    payment_count = 1
    benefit_str = u''
    payment_json = {
        'consequence': u'无限制',
        'dengdaiqi': u'无限制',
        'yuanyin': u'无限制',
        'beibaorennianling': u'无限制',
        'baodanniandu': u'无限制',
        'jifujine': u'无限制',
    }
    for line in benefit_line_arr:
        line_info = line.split('|')
        pid = int(line_info[0])
        sentence = line_info[1]
        is_title = int(line_info[2])
        consequence = int(line_info[3])
        dengdaiqi = int(line_info[4])
        dengdaiqi_value = line_info[5].strip()
        yuanyin = int(line_info[6])
        yuanyin_value = line_info[7].strip()
        beibaorennianling = int(line_info[8])
        beibaorennianling_value = line_info[9].strip()
        baodanniandu = int(line_info[10])
        baodanniandu_value = line_info[11].strip()
        jifujine = line_info[12]
        jifujine_value = line_info[13].strip()
        relation = int(line_info[14])
        # print line

        if is_title == 1:
            benefit_name = sentence
            benefit_consequence = consequence
            payment_json['consequence'] = benefit_consequence

        end_with_period_flag = False
        if sentence.rfind(u'。') > len(sentence)-2:
            end_with_period_flag = True

        if end_of_benefit_payment == False or waiting_for_first_period == True:
            benefit_str += sentence
            if dengdaiqi != 0:
                if len(dengdaiqi_value) > 0:
                    dengdaiqi_str += ' %s(%s)' % (dengdaiqi_dict[str(dengdaiqi)], dengdaiqi_value)
                else:
                    dengdaiqi_str += ' %s' % (dengdaiqi_dict[str(dengdaiqi)])
                payment_json['dengdaiqi'] = dengdaiqi_str
            if yuanyin != 0:
                yuanyin_str += ' ' + yuanyin_value
                payment_json['yuanyin'] = yuanyin_str
            if beibaorennianling != 0:
                if beibaorennianling == 1:
                    beibaorennianling_str += ' %s%s' % (beibaorennianling_value, beibaorennianling_dict[str(beibaorennianling)])
                elif beibaorennianling == 2:
                    beibaorennianling_str += ' %s%s' % (beibaorennianling_value, beibaorennianling_dict[str(beibaorennianling)])
                elif beibaorennianling == 3:
                    beibaorennianling_str += beibaorennianling_value.replace(',', beibaorennianling_dict[str(beibaorennianling)])
                elif beibaorennianling == 4:
                    beibaorennianling_str += ' %s%s' % (beibaorennianling_dict[str(beibaorennianling)], beibaorennianling_value)
                else:
                    beibaorennianling_str += beibaorennianling_value
                payment_json['beibaorennianling'] = beibaorennianling_str.strip()
            if baodanniandu != 0:
                if baodanniandu == 1:
                    baodanniandu_str += ' %s%s' % (baodanniandu_value, baodanniandu_dict[str(baodanniandu)])
                elif baodanniandu == 2:
                    baodanniandu_str += ' %s%s' % (baodanniandu_value, baodanniandu_dict[str(baodanniandu)])
                elif baodanniandu == 3:
                    baodanniandu_str += baodanniandu_value.replace(',', baodanniandu_dict[str(baodanniandu)])
                elif baodanniandu == 4:
                    baodanniandu_str += ' %s%s' % (baodanniandu_dict[str(baodanniandu)], baodanniandu_value)
                else:
                    baodanniandu_str += baodanniandu_value
                payment_json['baodanniandu'] = baodanniandu_str.strip()
            if relation != 0:
                jifujine_relation = relation
            if jifujine != '0':
                if jifujine_relation == 0:
                    if len(jifujine_value) > 0:
                        jifujine_str = '%sx%s' % (jifujine_translator(jifujine), jifujine_value)
                    else:
                        jifujine_str = '%s' % jifujine_translator(jifujine)
                    payment_json['jifujine'] = jifujine_str
                    if end_with_period_flag == True:
                        end_of_benefit_payment = True
                        waiting_for_first_period = False
                    else:
                        end_of_benefit_payment = False
                        waiting_for_first_period = True

                elif jifujine_relation == 1:
                    if jifujine_str == u'':
                        if len(jifujine_value) > 0:
                            jifujine_str = 'MAX( %sx%s,' % (jifujine_translator(jifujine), jifujine_value)
                        else:
                            jifujine_str = 'MAX( %s,' % jifujine_translator(jifujine)
                        end_of_benefit_payment = False
                        waiting_for_first_period = False
                    else:
                        if len(jifujine_value) > 0:
                            jifujine_str += '%sx%s )' % (jifujine_translator(jifujine), jifujine_value)
                        else:
                            jifujine_str += '%s )' % jifujine_translator(jifujine)
                        payment_json['jifujine'] = jifujine_str
                        if end_with_period_flag == True:
                            end_of_benefit_payment = True
                            waiting_for_first_period = False
                        else:
                            end_of_benefit_payment = False
                            waiting_for_first_period = True
                        
                else:
                    if jifujine_str == u'':
                        if len(jifujine_value) > 0:
                            jifujine_str = 'SUM( %sx%s,' % (jifujine_translator(jifujine), jifujine_value)
                        else:
                            jifujine_str = 'SUM( %s,' % jifujine_translator(jifujine)
                        end_of_benefit_payment = False
                        waiting_for_first_period = False
                    else:
                        if len(jifujine_value) > 0:
                            jifujine_str += '%sx%s )' % (jifujine_translator(jifujine), jifujine_value)
                        else:
                            jifujine_str += '%s )' % jifujine_translator(jifujine)
                        payment_json['jifujine'] = jifujine_str
                        if end_with_period_flag == True:
                            end_of_benefit_payment = True
                            waiting_for_first_period = False
                        else:
                            end_of_benefit_payment = False
                            waiting_for_first_period = True

            if waiting_for_first_period == True and end_with_period_flag == True:
                end_of_benefit_payment = True
                waiting_for_first_period = False


        if end_of_benefit_payment == True:
            # some exceptions to deal with
            if payment_json['dengdaiqi'].find(u'等待期外') != -1 and payment_json['yuanyin'].find('+') != -1:
                # split situation 1
                str_tmp = u'%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (pid, benefit_name, payment_count, u'无限制', u'意外', payment_json['beibaorennianling'], payment_json['baodanniandu'], payment_json['jifujine'], benefit_str)
                benefit_payments_combo_table.append(str_tmp)
                payment_count += 1

                # split situation 2
                str_tmp = u'%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (pid, benefit_name, payment_count, u'等待期外', u'非意外', payment_json['beibaorennianling'], payment_json['baodanniandu'], payment_json['jifujine'], benefit_str)
                benefit_payments_combo_table.append(str_tmp)
                payment_count += 1
                benefit_str = u''
            else:
                str_tmp = u'%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (pid, benefit_name, payment_json['consequence'], payment_count, payment_json['dengdaiqi'], payment_json['yuanyin'], payment_json['beibaorennianling'], payment_json['baodanniandu'], payment_json['jifujine'], benefit_str)
                benefit_payments_combo_table.append(str_tmp)
                payment_count += 1
                benefit_str = u''

            end_of_benefit_payment = False
            waiting_for_first_period = False
            dengdaiqi_str = u''
            yuanyin_str = u''
            beibaorennianling_str = u''
            baodanniandu_str = u''
            jifujine_str = u''
            jifujine_relation = 0
            payment_json = { 
                'consequence': u'无限制',
                'dengdaiqi': u'无限制',
                'yuanyin': u'无限制',
                'beibaorennianling': u'无限制',
                'baodanniandu': u'无限制',
                'jifujine': u'无限制',
            }
            payment_json['consequence'] = benefit_consequence

    if len(dengdaiqi_str) > 0 or len(yuanyin_str) > 0 or len(beibaorennianling_str) > 0 or len(baodanniandu_str) > 0 or len(jifujine_str) > 0:
        if payment_json['dengdaiqi'].find(u'等待期外') != -1 and payment_json['yuanyin'].find('+') != -1:
            # split situation 1
            str_tmp = u'%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (pid, benefit_name, payment_count, u'无限制', u'意外', payment_json['beibaorennianling'], payment_json['baodanniandu'], payment_json['jifujine'], benefit_str)
            benefit_payments_combo_table.append(str_tmp)
            payment_count += 1

            # split situation 2
            str_tmp = u'%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (pid, benefit_name, payment_count, u'等待期外', u'非意外', payment_json['beibaorennianling'], payment_json['baodanniandu'], payment_json['jifujine'], benefit_str)
            benefit_payments_combo_table.append(str_tmp)
            payment_count += 1
            benefit_str = u''
        else:
            str_tmp = u'%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (pid, benefit_name, payment_json['consequence'], payment_count, payment_json['dengdaiqi'], payment_json['yuanyin'], payment_json['beibaorennianling'], payment_json['baodanniandu'], payment_json['jifujine'], benefit_str)
            benefit_payments_combo_table.append(str_tmp)
            payment_count += 1
            benefit_str = u''

    return benefit_payments_combo_table

def analyze_product(product_line_arr):
    # analyzer_type:
    # 1-regular analyzer
    # 2-special analyzer dealing with complicated benefits TO BE IMPLEMENTED!

    def identify_benefit_complexity(benefit_line_arr):
        # benefit complexity sensors
        has_dengdaiqi_flag = False
        special_benefit_type_flag = False
        special_jifujine_type_flag = False
        for line in benefit_line_arr:
            line_info = line.split('|')
            pid = int(line_info[0])
            sentence = line_info[1]
            is_title = int(line_info[2])
            consequence = int(line_info[3])
            dengdaiqi = int(line_info[4])
            dengdaiqi_value = line_info[5].strip()
            yuanyin = int(line_info[6])
            yuanyin_value = line_info[7].strip()
            beibaorennianling = int(line_info[8])
            beibaorennianling_value = line_info[9].strip()
            baodanniandu = int(line_info[10])
            baodanniandu_value = line_info[11].strip()
            jifujine = line_info[12]
            jifujine_value = line_info[13].strip()
            relation = int(line_info[14])

            if is_title == 1 and consequence == 3:
                special_benefit_type_flag = True

            if dengdaiqi != 0:
                has_dengdaiqi_flag = True

            if jifujine.find('1') != -1 or jifujine.find('5') != -1:
                special_jifujine_type_flag = True

        return has_dengdaiqi_flag, special_benefit_type_flag, special_jifujine_type_flag

    product_benefit_payments_combo_table = []
    dengdaiqi_line_arr = []
    collect_flag = False
    for line in product_line_arr:
        line_info = line.split('|')
        pid = int(line_info[0])
        sentence = line_info[1]
        is_title = int(line_info[2])

        if sentence.find(u'等待期') != -1 and is_title == 2:
            collect_flag = True
            dengdaiqi_line_arr.append(line)
            continue

        if collect_flag == True and is_title != 0:
            collect_flag = False

        if collect_flag == True:
            dengdaiqi_line_arr.append(line)

    benefit_line_arr = []
    flush_flag = False
    collect_flag = False
    for line in product_line_arr:
        line_info = line.split('|')
        pid = int(line_info[0])
        sentence = line_info[1]
        is_title = int(line_info[2])
    
        if is_title != 0 and len(benefit_line_arr) > 0:
            flush_flag = True
        else:
            flush_flag = False
    
        if flush_flag == True:
            has_dengdaiqi_flag, special_benefit_type_flag, special_jifujine_type_flag = identify_benefit_complexity(benefit_line_arr)
            if len(dengdaiqi_line_arr) > 0:
                has_dengdaiqi_flag = True
            if special_benefit_type_flag == False and has_dengdaiqi_flag == True and special_jifujine_type_flag == True:
                ret = analyze_benefit_payments_special(benefit_line_arr, dengdaiqi_line_arr)
            else:
                ret = analyze_benefit_payments_regular(benefit_line_arr)
            product_benefit_payments_combo_table.extend(ret)
            benefit_line_arr = []
    
        if is_title == 1:
            collect_flag = True
        elif is_title == 2:
            collect_flag = False
        elif last_pid != pid:
            collect_flag = False
        else:
            pass
    
        if collect_flag == True:
            benefit_line_arr.append(line)

    if len(benefit_line_arr) > 0:
        has_dengdaiqi_flag, special_benefit_type_flag, special_jifujine_type_flag = identify_benefit_complexity(benefit_line_arr)
        if len(dengdaiqi_line_arr) > 0:
            has_dengdaiqi_flag = True
        if special_benefit_type_flag == False and has_dengdaiqi_flag == True and special_jifujine_type_flag == True:
            ret = analyze_benefit_payments_special(benefit_line_arr, dengdaiqi_line_arr)
        else:
            ret = analyze_benefit_payments_regular(benefit_line_arr)
        product_benefit_payments_combo_table.extend(ret)

    return product_benefit_payments_combo_table

input_file_path = argv[1]
input_file = open(input_file_path)
output_file = open(output_file_path, 'w')
str_tmp = u'%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % ('pid', 'benefit_name', 'consequence', 'payment_count', 'dengdaiqi', 'yuanyin', 'beibaorennianling', 'baodanniandu', 'jifujine', 'benefit_str')
output_file.write(str_tmp.encode('utf-8'))
product_line_arr = []
last_pid = -1
flush_flag = False
line_count = 0
target_pid = []
for line in input_file.readlines():
    line = line.strip().decode('utf-8')
    line_count += 1
    match = re.match(ur'pid\|', line)
    if match:
        continue

    if len(line) == 0:
        continue

    line_info = line.split('|')
    if len(line_info) < 15:
        print 'format error:', line.encode('utf-8')
        continue

    pid = int(line_info[0])
    sentence = line_info[1]
    is_title = int(line_info[2])

    if last_pid != pid and len(product_line_arr) > 0:
        flush_flag = True
    else:
        flush_flag = False

    if flush_flag == True:
        ret = analyze_product(product_line_arr)
        for line_tmp in ret:
            output_file.write(line_tmp.encode('utf-8'))
        product_line_arr = []

    product_line_arr.append(line)
    last_pid = pid

if len(product_line_arr) > 0:
    ret = analyze_product(product_line_arr)
    for line_tmp in ret:
        output_file.write(line_tmp.encode('utf-8'))

output_file.close()
