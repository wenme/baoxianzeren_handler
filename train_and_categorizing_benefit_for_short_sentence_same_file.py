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


if len(argv) < 3:
    print('''
    need 2 input parameters, the first one is training_file_path path(either TXT or XLSX), the second one is wordvecotr binary file path.
    training file needs code, sentence and label column.''')
    exit()

training_file_path = argv[1]
word2vec_file = argv[2]

embeddings_index = {}
w2v_model = word2vec.load(word2vec_file)
for word_obj in w2v_model.vocab:
    coefs = np.asarray(w2v_model[word_obj], dtype='float32')
    embeddings_index[word_obj] = coefs
print('found %d wordvectors~' % len(embeddings_index))

if training_file_path.find('.txt') == -1:
    benefit_material = pd.read_excel(training_file_path, header=0, index=None) # read the training material
else:
    code_arr = []
    sentence_arr = []
    label_arr= []
    f = open(training_file_path)
    content = f.read().decode('utf-8')
    f.close()
    try:
        line_count = 0
        for line in content.split('\n'):
            line_count += 1
            if line_count == 1:
                continue
            line = line.strip()
            if len(line) == 0:
                continue
            line_info = line.split('|')
            if len(line_info) < 3:
                continue
            code_arr.append(int(line_info[0]))
            sentence_arr.append(line_info[1])
            label_arr.append(int(line_info[2]))
        benefit_material = pd.DataFrame()
        benefit_material['code'] = np.asarray(code_arr)
        benefit_material['sentence'] = np.asarray(sentence_arr)
        benefit_material['label'] = np.asarray(label_arr)
    except Exception, e:
        print('ERR:', e, line)

print('%d reasonable samples loaded!' % len(benefit_material))

MAX_NUM_WORD = 20000
MAX_SEQUENCE_LEN = 100
EMBEDDING_DIM = 100

# word_splitting = lambda x: list(jieba.cut(x))
def word_splitting(x):
    ret_cut = jieba.cut(x)
    # print('src:', x)
    # print('cut:', ret_cut)
    return list(ret_cut)
benefit_material['words'] = benefit_material['sentence'].apply(word_splitting)
sample_pid = []
for i in range(0, len(benefit_material['code'])):
    pid = int(benefit_material['code'][i])
    if pid not in sample_pid:
        sample_pid.append(pid)

testing_split = 0.2
# test_pid = random.sample(sample_pid, int(len(sample_pid)*testing_split))
test_pid = [17443 , 17452 , 17455 , 17478 , 17479 , 17480 , 17487 , 17493 , 17498 , 17500 , 17506 , 17510 , 17540 , 17542 , 17545 , 17547]

words_arr = []
for i in benefit_material['words']:
    words_arr.extend(i)

words_dict_tmp = []
words_arr_distinct = list(set(words_arr))
words_index_len = len(words_arr_distinct)
print('total vocab size:%d' % words_index_len)
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
print('Shape of data tensor:', data.shape)
print('Shape of label tensor:', y.shape)

# seperate training part and testing part
train_sample = []
x_train = []
y_train = []
test_sample = []
x_test = []
y_test = []
for i in range(0, len(benefit_material['code'])):
    if int(benefit_material['code'][i]) not in test_pid:
        x_train.append(data[i])
        y_train.append(y[i])
        train_sample.append((benefit_material['code'][i], benefit_material['sentence'][i]))
    else:
        x_test.append(data[i])
        y_test.append(y[i])
        test_sample.append((benefit_material['code'][i], benefit_material['sentence'][i]))
x_train = np.asarray(x_train)
x_test = np.asarray(x_test)
y_train = np.asarray(y_train)
y_test = np.asarray(y_test)
print('training samples:', x_train.shape)
print('testing samples:', x_test.shape)
print('testing documents:', '%d/%d'%(len(test_pid), len(sample_pid)), test_pid)

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

saved_model_name = 'insurance_benefit_applying_docs.h5'
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
# model.fit(x_train, y_train, batch_size=32, epochs=20, validation_split=0.1)
model.fit(x_train, y_train, batch_size=32, epochs=20)
print('Complete training, and now saving model...\n')
model.save(saved_model_name)
del model

model = load_model(saved_model_name)
predict_rslt = model.predict(x_test)

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
std_ret = vec_col2category_col(y_test, category_arr)

output_file_path = 'test_input_output.txt'
output_file = open(output_file_path, 'w')
for i in range(0, len(ret)):
    output_line = '%s|%s|%s|%s\n' % (test_sample[i][0], test_sample[i][1], ret[i], std_ret[i])
    output_file.write(output_line.encode('utf-8'))
output_file.close()
