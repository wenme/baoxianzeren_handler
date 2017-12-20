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
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM, GRU

from keras.preprocessing.text import Tokenizer
from keras.layers import Dense, Input, Flatten
from keras.layers import Conv1D, MaxPooling1D, Embedding
from keras.models import Model


print('''=================================
本程序将计算「测试文件」内的句子是否保险金标题，输入训练文件如(train/for_training_300_with_benefit_type_and_payment_type_20170908.xlsx)，训练期间生成模型为'benfit_title_model.h5'
参数一：训练集，默认填写train/for_training_300_with_benefit_type_and_payment_type_20170908.xlsx
参数二：测试集，默认填写integrated_term_line.txt
参数三：词向量文件
输出文件：'benefit_title_output.txt'
''')

if len(argv) < 4:
    print('need 3 input parameters, the first one is training file, the second one is testing file, and the third one is wordvecotr binary file path')
    exit()

benefit_title_training_file_path = argv[1]
testing_file_path = argv[2]
word2vec_file = argv[3]

if testing_file_path.find('xlsx') == -1 and testing_file_path.find('txt') == -1:
    print('testing file must be xlsx or txt file type!')
    exit()

embeddings_index = {}
w2v_model = word2vec.load(word2vec_file)
for word_obj in w2v_model.vocab:
    coefs = np.asarray(w2v_model[word_obj], dtype='float32')
    embeddings_index[word_obj] = coefs
print('found %d wordvectors~' % len(embeddings_index))

benefit_material = pd.read_excel(benefit_title_training_file_path, header=0, index=None) # read the training material
print('%d reasonable samples loaded!' % len(benefit_material))

MAX_NUM_WORD = 20000
MAX_SEQUENCE_LEN = 100
EMBEDDING_DIM = 100

# def title_sn_stripping(x):
#     x = x.strip().replace(u'（', '').replace(u'）', '').replace(u'、', '')
#     x = re.sub(ur'^[0-9\.一二三四五六七八九十]', '', x)
#     return x
# benefit_material['sentence'] = benefit_material['sentence'].apply(title_sn_stripping)

def word_splitting(x):
    ret_cut = jieba.cut(x)
    return list(ret_cut)
benefit_material['words'] = benefit_material['sentence'].apply(word_splitting)

words_arr = []
for i in benefit_material['words']:
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
benefit_material['w2v'] = benefit_material['words'].apply(word2num) # this is the most tricky step to translate the whole words_arr into a int_arr for each line

data = sequence.pad_sequences(benefit_material['w2v'], maxlen=MAX_SEQUENCE_LEN)
category_arr = list(set(list(benefit_material['label'])))
category_dict = {}
for i in range(0, len(category_arr)):
    category_dict[category_arr[i]] = i
category_coding = lambda x: category_dict[x]
benefit_material['category_code'] = benefit_material['label'].apply(category_coding)
y = to_categorical(np.asarray(benefit_material['category_code']))

if testing_file_path.find('xlsx') != -1:
    testing_material = pd.read_excel(testing_file_path, header=0, index=None)
else:
    testing_file = open(testing_file_path)
    testing_file_code_arr = []
    testing_file_line_arr = []
    for line in testing_file.readlines():
        line = line.strip().decode('utf-8')
        line_info = line.split('|')
        if len(line_info) != 2:
            continue
        testing_file_code_arr.append(int(line_info[0]))
        testing_file_line_arr.append(line_info[1])
    testing_material = pd.DataFrame()
    testing_material['code'] = np.asarray(testing_file_code_arr)
    testing_material['sentence'] = np.asarray(testing_file_line_arr)
testing_material['words'] = testing_material['sentence'].apply(word_splitting)
testing_material['w2v'] = testing_material['words'].apply(word2num)
test_data = sequence.pad_sequences(testing_material['w2v'], maxlen=MAX_SEQUENCE_LEN)
print('training samples:', data.shape)
print('testing samples:', test_data.shape)

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

saved_model_name = './DeepLearning_model_h5_file/benfit_title_model.h5'

print('Training model.')
sequence_input = Input(shape=(MAX_SEQUENCE_LEN,), dtype='int32')
embedded_sequences = embedding_layer(sequence_input)
x = LSTM(128)(embedded_sequences)
x = Dense(64, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(64, activation='relu')(x)
x = Dense(64, activation='relu')(x)
preds = Dense(y.shape[1], activation='softmax')(x)

model = Model(sequence_input, preds)
model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['acc'])

# train section
# model.fit(data, y, batch_size=32, epochs=20, validation_split=0.1)
model.fit(data, y, batch_size=32, epochs=20)
print('Complete training, and now saving model...\n')
model.save(saved_model_name)
del model

model = load_model(saved_model_name)
predict_rslt = model.predict(test_data)

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

ret = vec_col2category_col(predict_rslt, category_arr)

output_file_path = 'benefit_title_output.txt'
output_file = open(output_file_path, 'w')
for i in range(0, len(ret)):
    output_line = '%s|%s|%s\n' % (testing_material['code'][i], testing_material['sentence'][i], 0 if len(testing_material['sentence'][i]) > 20 else ret[i])
    output_file.write(output_line.encode('utf-8'))
output_file.close()
