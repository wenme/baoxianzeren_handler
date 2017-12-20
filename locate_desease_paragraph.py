# -*- coding: utf-8 -*-

import re
import numpy as np
import pandas as pd
from sys import argv

import jieba #导入结巴分词
import word2vec
from keras.preprocessing import sequence
from keras.models import load_model

def refine_desease_list_name(name):
    name = name.strip().replace(u'：', '')

    match = re.match(ur'第?[一二三四五六七八九十零]+条? ?、?', name)
    if match:
        name = name.replace(match.group(0), '')

    match = re.match(ur'[0-9\.]+', name)
    if match:
        name = name.replace(match.group(0), '')

    name = name.replace(u'的释义', '')
    name = name.replace(u'的定义', '')
    name = name.replace(u'的种类及定义', '')
    name = name.replace(u'定义', '')
    name = name.replace(u'释义', '')
    return name

def find_desease_list_by_dl(array):
    saved_model_name = 'insurance_desease.h5'
    word2vec_file = '../insurance_wordvector_general.bin'
    MAX_NUM_WORD = 20000
    MAX_SEQUENCE_LEN = 100
    EMBEDDING_DIM = 100
    
    embeddings_index = {}
    w2v_model = word2vec.load(word2vec_file)
    for word_obj in w2v_model.vocab:
        coefs = np.asarray(w2v_model[word_obj], dtype='float32')
        embeddings_index[word_obj] = coefs
    
    df_tmp = pd.DataFrame()
    df_tmp['sentence'] = pd.Series(array)
    def word_splitting(x):
        ret_cut = jieba.cut(x)
        return list(ret_cut)
    df_tmp['words'] = df_tmp['sentence'].apply(word_splitting)
    
    words_arr = []
    for i in df_tmp['words']:
        words_arr.extend(i)
    
    words_dict_tmp = []
    words_arr_distinct = list(set(words_arr))
    words_index_len = len(words_arr_distinct)
    for i in range(0, words_index_len):
        word = words_arr_distinct[i]
        word_count = words_arr.count(word)
        words_dict_tmp.append((word_count, word))
    words_dict_tmp.sort(key=lambda x:x[0])
    words_dict_tmp.reverse()
    words_dict_tmp.insert(0, (-1, '0')) # to make sure the words count from index 1
    
    words_index = {}
    for i in range(0, len(words_dict_tmp)):
        words_index[words_dict_tmp[i][1]] = i
    del words_dict_tmp
    
    def word2num(words_row):
        rslt = []
        for word in words_row:
            try:
                rslt.append(words_index[word])
            except Exception, e:
                rslt.append(0)
        return rslt
    df_tmp['w2v'] = df_tmp['words'].apply(word2num)
    
    data = sequence.pad_sequences(df_tmp['w2v'], maxlen=MAX_SEQUENCE_LEN)
    model = load_model(saved_model_name)
    predict_rslt = model.predict(data)

    def revert_prediction(predict_rslt):
        ret = []
        for obj in predict_rslt:
            max_value = max(obj)
            max_value_pos = 0
            for v in obj:
                if v == max_value:
                    break
                else:
                    max_value_pos += 1
            ret.append(max_value_pos+1)
        return ret

    rslt = revert_prediction(predict_rslt)

    ret = []
    for i in range(0, len(rslt)):
        ret.append((array[i], rslt[i]))
    return ret

def find_desease_list_by_pattern(array, desease_arr):
    ret = []
    for line in array:
        target_desease = ''
        for obj in desease_arr:
            if line.find(obj) != -1 and len(line) < len(obj) + 7:
                if len(obj) > len(target_desease):
                    target_desease = obj
        if target_desease != '':
            ret.append(target_desease)
            
    return ret
 
def if_contain_desease_list(array, desease_arr):
    # print 'checking last %d sentences' % len(array),
    desease_list = []
    str_tmp = ' '.join(array)
    hit_count = 0
    for obj in desease_arr:
        match = re.search(ur'%s.*?[：指包括]{0,1}.*?。' % obj, str_tmp)
        if match:
            hit_count += 1
            desease_list.append(obj)

    if len(desease_list) > 2:
        # print 'over %d, ok' % len(desease_list),
        desease_list  = find_desease_list_by_pattern(array, desease_arr)
        return True, desease_list
    else:
        # print 'only %d, no ok' % len(desease_list),
        return False, desease_list

def is_suspect_title(sentence, desease_list_title_kw):
    for kw in desease_list_title_kw:
        if sentence.find(kw) != -1:
            if len(sentence) < 30:
                return True
    return False

print '''
本程序为了提取疾病列表，是以条款为单位，注意：输入文件需经过深度学习，即字段'label'已分辨出1为标题句子，否则为0。
本程序主要判断各个标题是否匹配疾病列表名单，如果是的话就输出疾病名单
'''

output_file = open('output/desease_output', 'w')
desease_arr = []
with open('desease_table') as desease_table:
    for line in desease_table.readlines():
        line = line.replace('\n', '').decode('utf-8')
        desease_arr.append(line)
desease_list_title_kw = [u'瘤', u'疾', u'病', u'癌']

excel_file = pd.read_excel(argv[1], header=0)
desease_list = []
last_code = 0
block_sentences = []
appending = False
for i in range(0, len(excel_file)):
    cur_code = excel_file['code'][i]
    sentence = excel_file['sentence'][i]
    label = excel_file['label'][i]

    # print cur_code, sentence, label, 
    if cur_code != last_code and appending:
        appending = False
        flag, desease_list_tmp = if_contain_desease_list(block_sentences, desease_arr)
        if flag:
            print 'BINGO:', last_code, refine_desease_list_name(block_sentences[0]), len(desease_list_tmp)
            for i in desease_list_tmp:
                print '\t', i
            # print 'end appending',

        block_sentences = []
        suspect_flag = is_suspect_title(sentence, desease_list_title_kw)
        if suspect_flag and label == 1:
            block_sentences.append(sentence)
            appending = True
            # print 'start appending',
        # print 'code diff'
    else:
        if appending and label != 1:
            block_sentences.append(sentence)
            # print 'appending and label not 1'
        elif appending and label == 1:
            flag, desease_list_tmp = if_contain_desease_list(block_sentences, desease_arr)
            if flag:
                print 'BINGO:', last_code, refine_desease_list_name(block_sentences[0]), len(desease_list_tmp)
                for i in desease_list_tmp:
                    print '\t', i
                # print 'end appending',
            appending = False
            block_sentences = []
            suspect_flag = is_suspect_title(sentence, desease_list_title_kw)
            if suspect_flag:
                block_sentences.append(sentence)
                appending = True
                # print 'start appending',
            # print 'appending and label 1'
        elif not appending and label == 1:
            block_sentences = []
            suspect_flag = is_suspect_title(sentence, desease_list_title_kw)
            if suspect_flag:
                block_sentences.append(sentence)
                appending = True
                # print 'start appending',
            # print 'not appending and label 1'
        else:
            # print 'else'
            pass
    last_code = cur_code

# buffer of last round in block_sentences will not be executed in loop
flag, desease_list_tmp = if_contain_desease_list(block_sentences, desease_arr)
if flag:
    print 'BINGO:', last_code, refine_desease_list_name(block_sentences[0]), len(desease_list_tmp)
    for i in desease_list_tmp:
        print '\t', i

output_file.close()
