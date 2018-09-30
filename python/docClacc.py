#coding=utf-8
import jieba
import re
import os
from pprint import pprint
from gensim import corpora, models


def convert_doc2word(str_content, cut_all):
    word_list = list(jieba.cut(str_content, cut_all= cut_all))
    return word_list

def rm_text(content):
    content = re.sub('\u3000','',content)
    return content

def get_stop_words(pathCN='', pathENG=''):
    with open(pathCN, 'r') as file:
        stopwordsCn = [l.strip() for l in file.readlines()]
    with open(pathENG, 'r') as file:
        stopwordsEng = [l.strip() for l in file.readlines()]
    stopwords = stopwordsCn + stopwordsEng
    for i in range(len(stopwords)):
        stopwords[i] = stopwords[i].decode('utf-8')
    return stopwords

def rm_tokens(words , stopWordCNPath='', stopWordENGPath=''):
    words_list = list(words)
    stop_words = get_stop_words(stopWordCNPath, stopWordENGPath)
    for i in range(words_list.__len__())[::-1]:
        if words_list[i] in stop_words:
            words_list.pop(i)
        elif words_list[i] in [' ',',','_']:
            words_list.pop(i)
    return words_list

files=["11111, 1,世界真的大，我想去看看","coremail很厉害了other been"]
words=[]
for file in files:
    words+=(convert_doc2word(file,False))
words=rm_tokens(words, 'data/stopCN.txt', 'data/stopENG.txt')
for w in words:
    print(w)
