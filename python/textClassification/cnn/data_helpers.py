#coding=utf8
import numpy as np
import re
import jieba
import pypinyin
from pypinyin import pinyin
import itertools
from collections import Counter

def stop_words():
    """
    读取停用词表
    """
    stop_words_file = open('../static/stop_words_ch.txt', 'r', encoding='gbk')
    stopwords_list = []
    for line in stop_words_file.readlines():
        stopwords_list.append(line[:-1])
    return stopwords_list

def jieba_fenci(raw, stopwords_list):
    """
    使用结巴分词把文件进行切分
    """
    text = ""
    word_list = list(jieba.cut(raw, cut_all=False))
    for word in word_list:
        if word not in stopwords_list and word != '\r\n':
            text += word
            text += ' '
    return text

def clean_str(string):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()


def load_data_and_labels(positive_data_file, negative_data_file):
    """
    Loads MR polarity data from files, splits the data into words and generates labels.
    Returns split sentences and labels.
    """
    # Load data from files
    positive_examples = list(open(positive_data_file, "r").readlines())
    positive_examples = [s.strip() for s in positive_examples]
    negative_examples = list(open(negative_data_file, "r").readlines())
    negative_examples = [s.strip() for s in negative_examples]
    # Split by words
    x_text = positive_examples + negative_examples
    x_text = [clean_str(sent) for sent in x_text]
    # Generate labels
    positive_labels = [[0, 1] for _ in positive_examples]
    negative_labels = [[1, 0] for _ in negative_examples]
    y = np.concatenate([positive_labels, negative_labels], 0)
    return [x_text, y]


def load_AI100_data_and_labels(data_path, use_pinyin=False):
    """
    用于多分类
    """
    x_text = []
    y = []
    stopwords_list = stop_words()
    with open(data_path, 'r') as f:
        for line in f:
            lable = int(line.split(',')[0])
            one_hot = [0]*11
            one_hot[lable-1] = 1
            y.append(np.array(one_hot))
            content = ""
            for aa in line.split(',')[1:]:
                content += aa
            text = jieba_fenci(content, stopwords_list)
            x_text.append(text)
    print ("data load finished")
    return [x_text, np.array(y)]

def load_data(data_path):
    """
    加载数据
    """
    x_text = []
    stopWordsList = stop_words()
    with open(data_path, 'r') as f:
        for line in f:
            text = jieba_fenci(line, stopWordsList)
            x_text.append(text)
    print("data load finished:",data_path.split('/')[-1])
    return x_text

def load_labels(length, classficationNum, onehotValue):
    """
    创建标签onehot码
    """
    labels= np.arange(length * classficationNum).reshape(length, classficationNum)
    for i in range(0, length):
        labels[i]=onehotValue
    return labels

def batch_iter(data, batch_size, num_epochs, shuffle=True):
    """
    为数据集生成一个批量iterator
    """
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int((len(data)-1)/batch_size) + 1
    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            yield shuffled_data[start_index:end_index]
