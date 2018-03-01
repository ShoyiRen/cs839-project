#!/usr/bin/python3
import string
import os
import re
import numpy
import sklearn
import random
from functools import partial
from sklearn import datasets, svm, metrics, tree, linear_model, ensemble
from sklearn.model_selection import cross_validate, StratifiedKFold, GridSearchCV
from sklearn.metrics import recall_score, precision_score, make_scorer

open_tag = '<L>'
closed_tag = '</L>'
special_chars = '.,/?;\'":!%&*()-+'

white_list = ["Rio de Janeiro", "Republic of Korea"]

def valid_example(words):
    try:
        words.encode('ascii')
    except UnicodeEncodeError:
        return False        # skip non-ascii phrases
    else:
        try:
            for w in white_list:
                if w in words: return True
            if has_stop_word(words) or len(words) <= len(open_tag):
                return False
            if not ((words[0].isupper() or (words[0] == '<' and words[len(open_tag)].isupper())) and \
                   words.count("'") == 0):
                return False
            
            for word in words.split(' '):
                if word[0].islower():
                    return False
            return True
        except:
            return False
        

def is_positive(word):
    open_count = word.count(open_tag)
    close_count = word.count(closed_tag)

    if open_count == 0 or open_count > 1 or \
       word[0] != '<' or close_count != open_count:
        return False
    loc = word.find(closed_tag)
    if ' ' in word[loc:]:
        return False
    word = word[:loc]
    return True

def has_stop_word(words):
    stop_words = [
        'a', 'i', 'in', 'from', 'for', 'the', 'does', 'have', 'who',
        'which', 'would', 'should', 'could', 'he', 'she', 'it', 'they',
        'is', 'am', 'are', 'can', 'and', 'you', 'on', 'this', 'that',
        'but', 'after'
    ]
    for word in words.split():
        if word.lower() in stop_words:
            return True
    return False 

def get_examples(file):
    examples = []
    for line in file:
        words = line.split(' ')
        num_words = len(words)
        for i in range(0, num_words):
            prev = ''
            succ = ''
            if i > 0: prev = words[i - 1]

            unigram = words[i]
            if valid_example(unigram):
                if i != num_words - 1: succ = words[i + 1]
                examples.append([unigram, prev, succ])

            if i > num_words - 2: continue
            bigram = words[i] + ' ' + words[i + 1]
            if valid_example(bigram):
                succ = ''
                if i != num_words - 2: succ = words[i + 2]
                examples.append([bigram, prev, succ])

            if i > num_words - 3: continue
            trigram = words[i] + ' ' + words[i + 1] + ' ' + words[i + 2]
            if valid_example(trigram):
                succ = ''
                if i != num_words - 3: succ = words[i + 3]
                examples.append([trigram, prev, succ])
    return examples

def remove_tags(lst):
    for i in range(0, len(lst)):
        lst[i] = lst[i].strip().replace(open_tag, '').replace(closed_tag, '')
    return lst

def has_sp_pre(prefix):
    special_prefix = set(['team','and','or','northern','southern','eastern','western','in',
        'from','to','of','defeated','defeats','defeat','beaten','beats','beat'])
    prefix = prefix.lstrip(string.punctuation)
    return prefix.lower() in special_prefix

def has_sp_pre_neg(prefix):
    special_prefix = set(['said'])
    prefix = prefix.lstrip(string.punctuation)
    return prefix.lower() in special_prefix

def has_sp_suf(suffix):
    special_suffix = set(['defeated','defeats','defeat','beaten','beats','beat'])
    suffix = suffix.rstrip(string.punctuation)
    if suffix.lower() in  special_suffix:
        return True
    elif re.match('19\d{2}', suffix) or re.match('20\d{2}', suffix):
        return True
    else:
        return False

def has_sp_suf_neg(suffix):
    special_suffix = set(['said', 'athlete'])
    suffix = suffix.rstrip(string.punctuation)
    if suffix.lower() in special_suffix:
        return True
    else:
        return False
        
def get_features_labels(examples):
    features = []
    labels = []
    examples_rm = []
    for ex in examples:
        skip = False
        word = ex[0].strip()
        if is_positive(word):
            loc = word.find(closed_tag)
            ex[0] = word[:loc]
            labels.append(1)
        else:
            for ch in word:
                if ch in special_chars:
                    skip = True
                    break
            if skip: continue
            labels.append(-1)

        ex_rm = remove_tags(ex)
        str_hash = hash(ex_rm[0])
        sp_pre = 1 if has_sp_pre(ex_rm[1]) else -1
        sp_pre_neg = 1 if has_sp_pre_neg(ex_rm[1]) else -1
        sp_suf = 1 if has_sp_suf(ex_rm[2]) else -1
        sp_suf_neg = 1 if has_sp_suf_neg(ex_rm[2]) else -1
        features.append([str_hash, sp_pre, sp_pre_neg, sp_suf_neg])
        examples_rm.append(ex_rm)

    ret =  list(map(list, zip(features, labels, examples_rm)))
    return ret

def test_score(clf, test_set):
    features_test = []
    labels_test = []
    words = []

    for filename in test_set:
        file = open(directory + filename, 'r')
        examples = get_features_labels(get_examples(file))
        for ex in examples:
            features_test.append(ex[0])
            labels_test.append(ex[1])
            words.append(ex[2][0])

    predicted = clf.predict(features_test)

    FNs = []
    for item, exp, word in zip(predicted, labels_test, words):
        if item != exp and exp == 1:
            FNs.append(word + ' labeled as ' + str(item))

    FNs.sort()
    #print('\n'.join(FNs))

    print("\ntest result for classifier %s:\n%s\n"
          % (clf, metrics.classification_report(labels_test, predicted)))

def cross_validation(clf, features, labels):
    precision_scorer = make_scorer(precision_score, pos_label=1)
    recall_scorer = make_scorer(recall_score, pos_label=1)
    scoring = {'precision_macro': precision_scorer,
               'recall_macro': recall_scorer}
    skf = StratifiedKFold(n_splits=5)
    scores = cross_validate(clf, features, labels, scoring=scoring,
                cv=skf, return_train_score=False)
    print('\nCV result for %s' % clf)
    precision = scores['test_precision_macro'].mean()
    recall = scores['test_recall_macro'].mean()
    print('precision = %f, recall = %f' % (precision, recall))
    print('f1 = %f' % ((2 * precision * recall) / (precision + recall)))


# training
directory = './data/'

#
# filenames = os.listdir(directory)
# random.seed(898033107)      # randomly drawn. credit: https://www.random.org/
# random.shuffle(filenames)
# I = filenames[:200]  # training set
# J = filenames[201:301]  # test set

f1 = open('train_set','r')
I = f1.readlines()
for i in range(0, len(I)):
    I[i] = I[i].rstrip('\n')
f1.close()

f2 = open('test_set','r')
J = f2.readlines()
for j in range(0, len(J)):
    J[j] = J[j].rstrip('\n')
f2.close()

features_train = []
labels_train = []

for filename in I:
    file = open(directory + filename, 'r')
    examples = get_features_labels(get_examples(file))
    for ex in examples: 
        features_train.append(ex[0])
        labels_train.append(ex[1])

classifiers = [
    linear_model.RidgeClassifierCV(normalize=True),    # Linear Regression (Ridge regression)
    linear_model.LogisticRegressionCV(),               # Logistic Regression
    tree.DecisionTreeClassifier(criterion='entropy'),  # Decision Tree
    ensemble.RandomForestClassifier(),                 # Random Forest
    svm.SVC(kernel='rbf')                              # SVM
]

for clf in classifiers:
    clf.fit(features_train, labels_train)
    cross_validation(clf, features_train, labels_train)
    test_score(clf, J)

