# -*- coding: utf-8 -*-

from __future__ import absolute_import #导入3.x的特征函数
from __future__ import print_function

import pandas as pd #导入Pandas
import numpy as np #导入Numpy
import jieba #导入结巴分词
import word2vec
import os, re
import random
from sys import argv

from keras.preprocessing import sequence
from keras.optimizers import SGD, RMSprop, Adagrad
from keras.utils import np_utils, to_categorical
from keras.models import Sequential, load_model
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.recurrent import LSTM, GRU

from keras.preprocessing.text import Tokenizer
from keras.layers import Input, Flatten
from keras.layers import Conv1D, MaxPooling1D, Embedding
from keras.models import Model

print('''
本程序为两层计算模型，第一层计算句子是否useful，第二层为单输入多输出模型，计算句子属性：
「既包含条件也包含金额」，字段标签为complete：0或1
「包含条件」，字段标签为condition：0或1
「包含金额」，字段标签为payment：0或1
输入训练文件跟part1一致，测试文件为part2的输出文本文件（默认为benefit_title_output.txt或benefit_title_output.xlsx），并生成两个模型文件part3_first_model_1i1o.h5、part3_second_model_1i3o.h5
输出文件问benefit_payment_output.txt
''')

if len(argv) < 4:
    print('need 3 input parameters, the first one is training_file_path(excel), the second one is testing_file_path(txt), the third one is wordvecotr binary file path')
    exit()

training_file_path = argv[1]
testing_file_path = argv[2]
word2vec_file = argv[3]

embeddings_index = {}
w2v_model = word2vec.load(word2vec_file)
for word_obj in w2v_model.vocab:
    coefs = np.asarray(w2v_model[word_obj], dtype='float32')
    embeddings_index[word_obj] = coefs
print('found %d wordvectors~' % len(embeddings_index))

sample_material = pd.read_excel(training_file_path, header=0, index=None) # read the training material
print('%d samples in total loaded!' % len(sample_material))

MAX_NUM_WORD = 20000
MAX_SEQUENCE_LEN = 100
EMBEDDING_DIM = 100

word_splitting = lambda x: list(jieba.cut(x))
sample_material['words'] = sample_material['sentence'].apply(word_splitting)
sample_pid = []
for i in range(0, len(sample_material['code'])):
    if int(sample_material['train_or_test'][i]) != 1:
        continue
    pid = int(sample_material['code'][i])
    if pid not in sample_pid:
        sample_pid.append(pid)

words_arr = []
for i in sample_material['words']:
    words_arr.extend(i)

words_dict_tmp = []
words_arr_distinct = list(set(words_arr))
words_index_len = len(words_arr_distinct)
print('total vocab size of training samples:%d' % words_index_len)
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
sample_material['w2v'] = sample_material['words'].apply(word2num) # this is the most tricky step to translate the whole words_arr into a int_arr for each line

# input_data
sample_data = sequence.pad_sequences(sample_material['w2v'], maxlen=MAX_SEQUENCE_LEN)

# useful_label
useful_arr = list(set(list(sample_material['useful'])))
category_dict = {}
for i in range(0, len(useful_arr)):
    category_dict[useful_arr[i]] = i
category_coding = lambda x: category_dict[x]
sample_material['useful_code'] = sample_material['useful'].apply(category_coding)
useful_label = to_categorical(np.asarray(sample_material['useful_code']))

# complete_label
complete_arr = list(set(list(sample_material['complete'])))
category_dict = {}
for i in range(0, len(complete_arr)):
    category_dict[complete_arr[i]] = i
sample_material['complete_code'] = sample_material['complete'].apply(category_coding)
complete_label = to_categorical(np.asarray(sample_material['complete_code']))

# condition_label
condition_arr = list(set(list(sample_material['condition'])))
category_dict = {}
for i in range(0, len(condition_arr)):
    category_dict[condition_arr[i]] = i
sample_material['condition_code'] = sample_material['condition'].apply(category_coding)
condition_label = to_categorical(np.asarray(sample_material['condition_code']))

# payment_label
payment_arr = list(set(list(sample_material['payment'])))
category_dict = {}
for i in range(0, len(payment_arr)):
    category_dict[payment_arr[i]] = i
sample_material['payment_code'] = sample_material['payment'].apply(category_coding)
payment_label = to_categorical(np.asarray(sample_material['payment_code']))

# null_label
null_arr = list(set(list(sample_material['null'])))
category_dict = {}
for i in range(0, len(null_arr)):
    category_dict[null_arr[i]] = i
sample_material['null_code'] = sample_material['null'].apply(category_coding)
null_label = to_categorical(np.asarray(sample_material['null_code']))

# second model training part
xx_train = []
yy_complete_train = []
yy_condition_train = []
yy_payment_train = []
yy_null_train = []

for i in range(0, len(sample_material['code'])):
    if int(sample_material['train_or_test'][i]) != 1:
        continue
    # useful == 1
    if int(sample_material['useful'][i]) == 1:
        xx_train.append(sample_data[i])
        yy_complete_train.append(complete_label[i])
        yy_condition_train.append(condition_label[i])
        yy_payment_train.append(payment_label[i])
        yy_null_train.append(null_label[i])
xx_train = np.asarray(xx_train)
yy_complete_train = np.asarray(yy_complete_train)
yy_condition_train = np.asarray(yy_condition_train)
yy_payment_train = np.asarray(yy_payment_train)
yy_null_train = np.asarray(yy_null_train)

# get test data
if testing_file_path.find(u'.txt') != -1:
    print('TXT file detected.')
    x_test_code = []
    x_test_sentence = []
    x_test_is_title = []
    x_test_benefit_type = []
    testing_file = open(testing_file_path)
    for line in testing_file.readlines():
        line = line.decode('utf-8').replace('\n', '')
        line_info = line.split('|')
        if len(line_info) < 4:
            continue
        x_test_code.append(int(line_info[0]))
        x_test_sentence.append(line_info[1])
        x_test_is_title.append(int(line_info[2]))
        x_test_benefit_type.append(line_info[3])
    
    testing_material = pd.DataFrame()
    testing_material['code'] = np.asarray(x_test_code)
    testing_material['sentence'] = np.asarray(x_test_sentence)
    testing_material['is_title'] = np.asarray(x_test_is_title)
    testing_material['benefit_type'] = np.asarray(x_test_benefit_type)
    testing_material['words'] = testing_material['sentence'].apply(word_splitting)
    testing_material['w2v'] = testing_material['words'].apply(word2num)
    test_data = sequence.pad_sequences(testing_material['w2v'], maxlen=MAX_SEQUENCE_LEN)
elif testing_file_path.find(u'.xls') != -1:
    print('excel file detected.')
    testing_material = pd.read_excel(testing_file_path, header=0)
    testing_material['words'] = testing_material['sentence'].apply(word_splitting)
    testing_material['w2v'] = testing_material['words'].apply(word2num)
    if u'is_title' not in testing_material.columns:
        testing_material['is_title'] = [0 for i in range(0,len(testing_material))]
    if u'benefit_type' not in testing_material.columns:
        testing_material['benefit_type'] = [0 for i in range(0,len(testing_material))]
    test_data = sequence.pad_sequences(testing_material['w2v'], maxlen=MAX_SEQUENCE_LEN)
else:
    print('testing file format error!!')
    exit()

print('model1 training samples:', sample_data.shape)
print('model2 training samples:', xx_train.shape)
print('testing samples:', test_data.shape)

# building embedding matrix as the Embedding Layer initial weights
num_words = min(MAX_NUM_WORD, len(words_index)+1)
embedding_matrix = np.zeros((num_words, EMBEDDING_DIM))

for word, i in words_index.items():
    if i > len(words_index):
        continue
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        embedding_matrix[i] = embedding_vector

embedding_layer = Embedding(num_words,
                            EMBEDDING_DIM,
                            weights=[embedding_matrix],
                            input_length=MAX_SEQUENCE_LEN,
                            trainable=False)

# building first model=====================================================
first_model_name = 'part3_first_model_1i1o.h5'
print('Training first model.')
sequence_input = Input(shape=(MAX_SEQUENCE_LEN, ), dtype='int32')
embedded_sequences = embedding_layer(sequence_input)
x = LSTM(128)(embedded_sequences)
x = Dense(64, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(64, activation='relu')(x)
x = Dense(64, activation='relu')(x)
preds = Dense(useful_label.shape[1], activation='softmax')(x)

model = Model(sequence_input, preds)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['acc'])

# training first model
# model.fit(x_train, y_train, batch_size=32, epochs=30, validation_split=0.1)
model.fit(sample_data, useful_label, batch_size=32, epochs=30)
print('Complete training, and now saving first model to \"%s\"...\n' % first_model_name)
model.save(first_model_name)
del model

# building second model====================================================
second_model_name = 'part3_second_model_1i4o.h5'
print('Training second model.')
main_input = Input(shape=(MAX_SEQUENCE_LEN, ), dtype='int32', name='main_input')
x = Embedding(num_words, EMBEDDING_DIM, weights=[embedding_matrix], input_length=MAX_SEQUENCE_LEN, trainable=False)(main_input)
x = LSTM(128)(x)
x = Dense(64, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(64, activation='relu')(x)
x = Dense(64, activation='relu')(x)

complete_output = Dense(complete_label.shape[1], activation='softmax', name='1')(x)
condition_output = Dense(condition_label.shape[1], activation='softmax', name='2')(x)
payment_output = Dense(payment_label.shape[1], activation='softmax', name='3')(x)
null_output = Dense(null_label.shape[1], activation='softmax', name='4')(x)

model = Model(inputs=[main_input], outputs=[complete_output, condition_output, payment_output, null_output])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])
model.fit([xx_train], [yy_complete_train, yy_condition_train, yy_payment_train, yy_null_train], epochs=30, batch_size=32)
print('Complete training, and now saving second model to \"%s\"...\n' % second_model_name)
model.save(second_model_name)
del model

# revert the output back to normal category
def vec_col2category_col(vec_col, category_arr):
    ret = []
    for obj in vec_col:
        max_value = max(obj)
        max_value_pos = 0
        for v in obj:
            if v == max_value:
                break
            else:
                max_value_pos += 1
        ret.append(category_arr[max_value_pos])
    return ret
print('now doing prediction,', end=' ')
model1 = load_model(first_model_name)
preds = model1.predict(test_data)
model1_ret = vec_col2category_col(preds, useful_arr)

model2 = load_model(second_model_name)
preds = model2.predict(test_data)
model2_ret1 = vec_col2category_col(preds[0], complete_arr)
model2_ret2 = vec_col2category_col(preds[1], condition_arr)
model2_ret3 = vec_col2category_col(preds[2], payment_arr)
model2_ret4 = vec_col2category_col(preds[3], null_arr)

output_file_path = 'benefit_payment_output.txt'
print('and saving result to file: %s' % output_file_path)
output_file = open(output_file_path, 'w')
output_line = '%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % ('code', 'sentence', 'useful', 'complete', 'condition', 'payment', 'null', 'is_title', 'benefit_type')
output_file.write(output_line.encode('utf-8'))
for i in range(0, len(test_data)):
    output_line = '%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (testing_material['code'][i], testing_material['sentence'][i], model1_ret[i], model2_ret1[i], model2_ret2[i], model2_ret3[i], model2_ret4[i], testing_material['is_title'][i], testing_material['benefit_type'][i])
    output_file.write(output_line.encode('utf-8'))
output_file.close()
