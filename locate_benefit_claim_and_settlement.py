# -*- coding: utf-8 -*-

import re
import numpy as np
import pandas as pd
from sys import argv

def str2int(str_tmp):
    match = re.search(ur'([0-9]+)', str_tmp)
    if match:
        return int(match.group(0))

    match = re.search(ur'([零一二三四五六七八九十百千]+)', str_tmp)
    if match:
        str_num = match.group(0)
        chn_num_dict = {
            u'零': 0,
            u'一': 1,
            u'二': 2,
            u'三': 3,
            u'四': 4,
            u'五': 5,
            u'六': 6,
            u'七': 7,
            u'八': 8,
            u'九': 9,
            u'十': 10,
            u'百': 100,
            u'千': 1000
        }
        if str_num[0] == u'十':
            str_num += u'一'
        value = 0
        cur_v = 0
        for chn_num in str_num:
            v = chn_num_dict[chn_num]
            if v == 0:
                continue
            elif v < 10:
                cur_v = v
            else:
                value += cur_v * chn_num_dict[chn_num]
                cur_v = 0
        value += cur_v
        return value

    return None

def get_ne_arr_by_event(event):
    switcher = {
        u'投保年龄':['tenor', 'age', ],
        u'续保年龄':['age',],
        u'犹豫期':['tenor',],
        u'保险金申请资料':['identity','policy_benefit','document',],
        u'宽限期':['tenor',],
        u'保险期间':['age','tenor',],
        u'最低保证利率':['percentage',],
        u'等待期':['tenor',],
        u'退保资料':['document',],
        u'退保给付':['tenor',],
        u'退保费用':['percentage',],
        u'事故通知期限':['tenor',],
        u'诉讼时效':['tenor',],
        u'保险金批核期限':['tenor',],
        u'保险金给付期限':['tenor',],
        u'年金开始领取日':['age',],
        u'退保给付':['tenor',],
        u'退保费用':['percentage',],
    }
    return switcher.get(event, [])

def get_ne_pattern_by_name(ne_name):
    switcher = {
        'percentage': [
            '([0-9\.]+%)',
            '(百分之[一二三四五六七八九十])',
        ],
        'age': [
            '([0-9一二三四五六七八九十百千]+[周岁日]+)',
        ],
        'tenor': [
            '([0-9一二三四五六七八九十百千]+[个自然日天月年]+)',
            '终身',
        ],
    }
    return switcher.get(ne_name, [])

def insurance_age_coverage_handler(sentence, event):
    pattern = u'([0-9一二三四五六七八九十百千]+[周岁]+)'
    match = re.findall(ur'%s'%pattern, sentence)
    age_arr = []
    if match:
        for obj in match:
            age_arr.append((obj, str2int(obj)))

    if len(age_arr) == 0:
        return None, None

    age_arr = list(set(age_arr))
    age_arr.sort(key=lambda x:x[1])
    if len(age_arr) == 1:
        pattern = u'([0-9一二三四五六七八九十百千]+[天日]+)'
        match = re.findall(ur'%s'%pattern, sentence)
        time_arr = []
        if match:
            for obj in match:
                time_arr.append((obj, str2int(obj)))
            time_arr.sort(key=lambda x:x[1])
            return time_arr[0][0], age_arr[0][0]
        else:
            return u'0周岁', age_arr[0][0]
    else:
        return age_arr[0][0], age_arr[-1][0]

def insurance_max_renewal_age(sentence, event):
    for ne in get_ne_arr_by_event(event):
        for pattern in get_ne_pattern_by_name(ne):
            pattern = pattern.decode('utf-8')
            match = re.search(ur'%s'%(pattern), sentence)
            if match:
                return match.group(0)
    return 'NO'

def insurance_duration_handler(sentence, event):
    duration_arr = []
    for ne in get_ne_arr_by_event(event):
        for pattern in get_ne_pattern_by_name(ne):
            pattern = pattern.decode('utf-8')
            match = re.findall(ur'%s'%(pattern), sentence)
            for obj in match:
                duration_arr.append(obj)
    return ','.join(duration_arr)

def insurance_cool_off_period(sentence, event):
    for ne in get_ne_arr_by_event(event):
        for pattern in get_ne_pattern_by_name(ne):
            pattern = pattern.decode('utf-8')
            match = re.search(ur'%s'%(pattern), sentence)
            if match:
                return match.group(0)
    return 'NO'

def insurance_grace_period(sentence, event):
    for ne in get_ne_arr_by_event(event):
        for pattern in get_ne_pattern_by_name(ne):
            pattern = pattern.decode('utf-8')
            match = re.findall(ur'%s'%(pattern), sentence)
            if len(match) == 1:
                return match[0]
            elif len(match) > 1:
                for obj in match:
                    if obj.find(u'天') != -1 or obj.find(u'日') != -1:
                        return obj
            else:
                pass
                    
    return 'NO'

def insurance_min_interest_rate(sentence, event):
    rate_arr = []
    for ne in get_ne_arr_by_event(event):
        for pattern in get_ne_pattern_by_name(ne):
            pattern = pattern.decode('utf-8')
            match = re.findall(ur'%s'%(pattern), sentence)
            for obj in match:
                rate_arr.append(obj)
    return ','.join(rate_arr)

def insurance_waiting_period(sentence, event):
    for ne in get_ne_arr_by_event(event):
        for pattern in get_ne_pattern_by_name(ne):
            pattern = pattern.decode('utf-8')
            match = re.search(ur'%s'%(pattern), sentence)
            if match:
                return match.group(0)
    return 'NO'

def insurance_litigation_period(sentence, event):
    for ne in get_ne_arr_by_event(event):
        for pattern in get_ne_pattern_by_name(ne):
            pattern = pattern.decode('utf-8')
            match = re.search(ur'%s'%(pattern), sentence)
            if match:
                return match.group(0)
    return 'NO'

def insurance_accident_notify_period(sentence, event):
    for ne in get_ne_arr_by_event(event):
        for pattern in get_ne_pattern_by_name(ne):
            pattern = pattern.decode('utf-8')
            match = re.search(ur'%s'%(pattern), sentence)
            if match:
                return match.group(0)
    return 'NO'

def insurance_benefit_approval_period(sentence, event):
    period_arr = []
    for ne in get_ne_arr_by_event(event):
        for pattern in get_ne_pattern_by_name(ne):
            pattern = pattern.decode('utf-8')
            match = re.findall(ur'%s'%(pattern), sentence)
            for obj in match:
                period_arr.append(obj)
    return ','.join(period_arr)

def insurance_benefit_pay_period(sentence, event):
    for ne in get_ne_arr_by_event(event):
        for pattern in get_ne_pattern_by_name(ne):
            pattern = pattern.decode('utf-8')
            match = re.search(ur'%s'%(pattern), sentence)
            if match:
                return match.group(0)
    return 'NO'

def insurance_annuity_claim_age(sentence, event):
    age_arr = []
    pattern = u'([0-9一二三四五六七八九十百千]+[周岁个保单年度、和]+)'
    match = re.findall(ur'%s'%(pattern), sentence)
    for obj in match:
        age_arr.append(obj.replace(u'和', u'、').replace(u'、', u'周岁'))
    return ','.join(age_arr)

def insurance_surrender_period(sentence, event):
    for ne in get_ne_arr_by_event(event):
        for pattern in get_ne_pattern_by_name(ne):
            pattern = pattern.decode('utf-8')
            match = re.search(ur'%s'%(pattern), sentence)
            if match:
                return match.group(0)
    return 'NO'

def insurance_surrender_fee(sentence, event):
    fee_arr = []
    for ne in get_ne_arr_by_event(event):
        for pattern in get_ne_pattern_by_name(ne):
            pattern = pattern.decode('utf-8')
            match = re.findall(ur'%s'%(pattern), sentence)
            for obj in match:
                fee_arr.append(obj)
    return ','.join(fee_arr)

def insurance_payment_info(sentence, event):
    payment_arr = []
    if sentence.find(u'一次') != -1 or sentence.find(u'趸交') != -1:
        payment_arr.append(u'趸交')
    if sentence.find(u'转入') != -1:
        payment_arr.append(u'转入')
    if sentence.find(u'首次') != -1:
        payment_arr.append(u'首次')
    if sentence.find(u'追加') != -1:
        payment_arr.append(u'追加')
    pattern = u'([0-9一二三四五六七八九十百千]+年)'
    match = re.findall(ur'%s'%(pattern), sentence)
    if len(match) > 0:
        installment_str = ','.join(match)
        payment_arr.append(u'分期：'+installment_str)
    elif sentence.find(u'分期') != -1:
        payment_arr.append(u'分期')
    else:
        pass

    if len(payment_arr) > 0:
        return ','.join(payment_arr)
    else:
        return 'NO'

if len(argv) < 3:
    print('need 2 input parameters, the first one is source excel file path, the second one is output file path')
    exit()

excel_file = argv[1]
output_file = open(argv[2], 'w')
excel_content = pd.read_excel(excel_file, header=0, index=None) # read the excel file


for i in range(0, len(excel_content)):
    sentence = excel_content['sentence'][i]
    event = excel_content['label'][i]
    pid = str(excel_content['code'][i])

    if event == u'投保年龄':
        min_age, max_age = insurance_age_coverage_handler(sentence, event)
        if min_age == None:
            str_tmp = pid + '|' + sentence + '|' + event + '|' + 'NO' + '\n'
        else:
            str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s,%s'%(min_age, max_age) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'续保年龄':
        renewal_age_str = insurance_max_renewal_age(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(renewal_age_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'保险期间':
        duration_str = insurance_duration_handler(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(duration_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'犹豫期':
        cool_off_str = insurance_cool_off_period(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(cool_off_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'宽限期':
        grace_period_str = insurance_grace_period(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(grace_period_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'最低保证利率':
        rate_str = insurance_min_interest_rate(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(rate_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'等待期':
        waiting_period_str = insurance_waiting_period(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(waiting_period_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'诉讼时效':
        litigation_period_str = insurance_litigation_period(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(litigation_period_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'事故通知期限':
        accident_notify_period_str = insurance_accident_notify_period(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(accident_notify_period_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'保险金批核期限':
        approval_period_str = insurance_benefit_approval_period(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(approval_period_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'保险金给付期限':
        pay_period_str = insurance_benefit_pay_period(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(pay_period_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'年金开始领取日':
        age_str = insurance_annuity_claim_age(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(age_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'退保给付':
        surrender_period_str = insurance_surrender_period(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(surrender_period_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'交费方式与期限':
        payment_str = insurance_payment_info(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(payment_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

    if event == u'退保费用':
        fee_str = insurance_surrender_fee(sentence, event)
        str_tmp = pid + '|' + sentence + '|' + event + '|' + u'%s'%(fee_str) + '\n'
        output_file.write(str_tmp.encode('utf-8'))

output_file.close()
