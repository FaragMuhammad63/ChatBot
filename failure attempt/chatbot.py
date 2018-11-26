import re
import time

import numpy as np
import tensorflow as tf

# getting the data from 'data.txt' file
f = open('data.txt', 'r', encoding='utf-8')
lines = f.readlines()
f.close()

# data processing
counter = 0
questions = []
answers = []
for line in lines:
    temp = line.split(' +++$+++ ')
    if counter == 0:
        counter += 1
        continue
    questions.append(temp[0].replace('\n', ''))
    answers.append(temp[1].replace('\n', ''))
    counter += 1


# cleaning text to be easy for using
def clean_text(text):
    text = text.lower()
    text = re.sub("'d", " would", text)
    text = re.sub("'s", " is", text)
    text = re.sub("'m", " am", text)
    text = re.sub("'re", " are", text)
    text = re.sub("'ll", " will", text)
    text = re.sub("'ve", " have", text)
    text = re.sub("won't", "will not", text)
    text = re.sub("let's", "lets", text)
    text = re.sub("n't", " not", text)
    text = re.sub('[-()\"*#/@;:<>{}\[\]+|~.?`,=\'!]', " ", text)
    re.sub(' +', ' ', text)
    text = re.sub(" lets ", " let's ", text)
    return text


# cleaning the questions
clean_questions = []
for question in questions:
    clean_questions.append(clean_text(question))

# cleaning the answers
clean_answers = []
for answer in answers:
    clean_answers.append(clean_text(answer))

# mapping each word to its number of occurrences
word_count = {}
for question in clean_questions:
    for word in question.split(' '):
        if word not in word_count:
            word_count[word] = 1
        else:
            word_count[word] += 1
for answer in clean_answers:
    for word in answer.split(' '):
        if word not in word_count:
            word_count[word] = 1
        else:
            word_count[word] += 1

# removing empty string from words
word_count.pop('')

# mapping question words and answer words to unique number
# threshold = int(0.05 * sum([word_count[i] for i in word_count.keys()])) --> to large number try 20
threshold = 20
question_words_id = {}
word_id = 0
for word, count in word_count.items():
    if count >= threshold:
        question_words_id[word] = word_id
        word_id += 1

answer_words_id = {}
for word, count in word_count.items():
    if count >= threshold:
        answer_words_id[word] = word_id
        word_id += 1

# <PAD> Padding
# <EOS> end of statement
# <OUT> out of common words
# <SOS> start of statement
tokens = ['<PAD>', '<EOS>', '<UNK>', '<GO>']
for token in tokens:
    question_words_id[token] = len(question_words_id) + 1
for token in tokens:
    answer_words_id[token] = len(answer_words_id) + 1

words_answer_id = {}
for word in answer_words_id:
    words_answer_id[answer_words_id[word]] = word

for i in range(len(clean_answers)):
    clean_answers[i] += '<EOS>'

# translate the questions to their words ids
questions_translated = []
for q in clean_questions:
    ids = []
    for word in q.split():
        if word not in question_words_id.keys():
            ids.append(question_words_id['<UNK>'])
        else:
            ids.append(question_words_id[word])
    questions_translated.append(ids)

# translate the answers to their words ids
answers_translated = []
for q in clean_answers:
    ids = []
    for word in q.split():
        if word not in answer_words_id.keys():
            ids.append(answer_words_id['<UNK>'])
        else:
            ids.append(answer_words_id[word])
    answers_translated.append(ids)

maximum_question_length = max([len(x) for x in questions_translated])

# sorting the questions and answers depending on question length
# these two lists holds sorted questions and answers indices
sorted_questions = []
sorted_answers = []
for i in range(1, maximum_question_length + 1):
    for el in enumerate(questions_translated):
        if len(el[1]) == i:
            sorted_questions.append(questions_translated[el[0]])
            sorted_answers.append(answers_translated[el[0]])


# Building seq2seq model
# Creating placeholders for the inputs and the targets
def model_inputs():
    inputs = tf.placeholder(tf.int32, [None, None], name = 'input')
    targets = tf.placeholder(tf.int32, [None, None], name = 'target')
    lr = tf.placeholder(tf.float32, name = 'learning_rate')
    keep_prob = tf.placeholder(tf.float32, name = 'keep_prob')
    return inputs, targets, lr, keep_prob

# Preprocessing the targets
def preprocess_targets(targets, word2int, batch_size):
    left_side = tf.fill([batch_size, 1], word2int['<GO>'])
    right_side = tf.strided_slice(targets, [0,0], [batch_size, -1], [1,1])
    preprocessed_targets = tf.concat([left_side, right_side], 1)
    return preprocessed_targets

# I was following a course trying to build chatbot from scratch and I have been stucked here.........