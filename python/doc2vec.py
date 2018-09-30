import os
import numpy as np 
import gensim
from gensim.models.doc2vec import Doc2Vec, LabeledSentence
from sklearn.cross_validation import train_test_split
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
def get_dataset():
    with open("C:\\Users\\admin\\Desktop\\logAnalyze\\src\\python\\data\\aclImdb_v1\\aclImdb\\train\\pos.txt",'r') as infile:
        pos_reviews = infile.readlines()
    with open("C:\\Users\\admin\\Desktop\\logAnalyze\\src\\python\\data\\aclImdb_v1\\aclImdb\\train\\neg.txt",'r') as infile:
        neg_reviews = infile.readlines()
    with open("C:\\Users\\admin\\Desktop\\logAnalyze\\src\\python\\data\\aclImdb_v1\\aclImdb\\train\\unsup.txt",'r') as infile:
        unsup_reviews = infile.readlines()
    y = np.concatenate((np.ones(len(pos_reviews)), np.zeros(len(neg_reviews))))
    x_train, x_test, y_train, y_test = train_test_split(np.concatenate((pos_reviews, neg_reviews)), y, test_size=0.2)

    def cleanText(corpus):
        punctuation = """.,?!:;(){}[]_"""
        corpus = [z.lower().replace('\n','') for z in corpus]
        corpus = [z.replace('<br />', ' ') for z in corpus]

        for c in punctuation:
            corpus = [z.replace(c, ' %s '%c) for z in corpus]
        corpus = [z.split() for z in corpus]
        return corpus

    x_train = cleanText(x_train)
    x_test = cleanText(x_test)
    unsup_reviews = cleanText(unsup_reviews)

    def labelizeReviews(reviews, label_type):
        labelized = []
        for i,v in enumerate(reviews):
            label = '%s_%s'%(label_type,i)
            labelized.append(LabeledSentence(v, [label]))
        return labelized

    x_train = labelizeReviews(x_train, 'TRAIN')
    x_test = labelizeReviews(x_test, 'TEST')
    unsup_reviews = labelizeReviews(unsup_reviews, 'UNSUP')

    return x_train,x_test,unsup_reviews,y_train, y_test

def getVecs(model, corpus, size):
    vecs = [ np.array(model.docvecs[z.tags[0]]).reshape((1, size)) for z in corpus]
    return np.concatenate(vecs)

def train(x_train,x_test,unsup_reviews,size = 400,epoch_num=10):
    model_dm = gensim.models.Doc2Vec(min_count=1, window=10, size=size, sample=1e-3, negative=5, workers=3)
    model_dbow = gensim.models.Doc2Vec(min_count=1, window=10, size=size, sample=1e-3, negative=5, dm=0, workers=3)

    model_dm.build_vocab(x_train+ x_test+ unsup_reviews)
    model_dbow.build_vocab(x_train+ x_test+ unsup_reviews)

    all_train_reviews = x_train+ unsup_reviews
    for epoch in range(epoch_num):
        #perm = np.random.permutation(np.array(all_train_reviews).shape[0])
        model_dm.train(all_train_reviews, epochs=model_dm.epochs,total_examples=model_dm.corpus_count)
        model_dbow.train(all_train_reviews, epochs=model_dbow.epochs, total_examples=model_dbow.corpus_count)
    
    print("step 2")
    x_test = np.array(x_test)
    for epoch in range(epoch_num):
        perm = np.random.permutation(x_test.shape[0])
        model_dm.train(x_test[perm])
        model_dbow.train(x_test[perm])

    return model_dm,model_dbow

def get_vectors(model_dm,model_dbow):

    train_vecs_dm = getVecs(model_dm, x_train, size)
    train_vecs_dbow = getVecs(model_dbow, x_train, size)
    train_vecs = np.hstack((train_vecs_dm, train_vecs_dbow))

    test_vecs_dm = getVecs(model_dm, x_test, size)
    test_vecs_dbow = getVecs(model_dbow, x_test, size)
    test_vecs = np.hstack((test_vecs_dm, test_vecs_dbow))

    return train_vecs,test_vecs

def Classifier(train_vecs,y_train,test_vecs, y_test):
    from sklearn.linear_model import SGDClassifier

    lr = SGDClassifier(loss='log', penalty='l1')
    lr.fit(train_vecs, y_train)

    print ('Test Accuracy: %.2f'%lr.score(test_vecs, y_test))

    return lr



def ROC_curve(lr,y_test):
    from sklearn.metrics import roc_curve, auc
    import matplotlib.pyplot as plt

    pred_probas = lr.predict_proba(test_vecs)[:,1]

    fpr,tpr,_ = roc_curve(y_test, pred_probas)
    roc_auc = auc(fpr,tpr)
    plt.plot(fpr,tpr,label='area = %.2f' %roc_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])

    plt.show()

if __name__ == "__main__":
    size,epoch_num = 400,10
    x_train,x_test,unsup_reviews,y_train, y_test = get_dataset()
    print("get dataset")
    model_dm,model_dbow = train(x_train,x_test,unsup_reviews,size,epoch_num)
    print("train succeed")
    train_vecs,test_vecs = get_vectors(model_dm,model_dbow)
    lr=Classifier(train_vecs,y_train,test_vecs, y_test)
    ROC_curve(lr,y_test)