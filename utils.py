# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
import numpy.random
import numpy as np
import time
import datetime
import json
import os
class Recorder:

    def __init__(self,args):
        self.record=[]
        self.text_name = 'khan_topic_{0}.npy'.format(args.name)
    def update(self,epoch,task_solution,test_performance):
        self.record.append([epoch, task_solution, test_performance])
        np.save(self.text_name, self.record)
    def all_records(self):
        return self.record

def shuffle_datapoints(questions,labels):

    shuffle_ids = np.random.permutation(len(questions))
    questions = np.array(questions)[shuffle_ids]
    labels = np.array(labels)[shuffle_ids]
    return questions,labels

def get_validation_set(questions,labels,args):

    questions, labels = shuffle_datapoints(questions, labels)
    index = args.batch_size * args.valid_size

    return questions[:index], labels[:index]

def get_wrong_triples(results,triples):
    wrong_triples = []
    for ii in range(len(results)):
        if results[ii][0] == False:
            wrong_triple = []
            for tt in range(3):
                if tt==0:
                    wrong_triple.append(triples[ii][tt])
                else:
                    wrong_triple.append(triples[ii][tt])
                    wrong_triple.append(results[ii][tt])
            wrong_triples.append(wrong_triple)
    return wrong_triples

def data_process(args):
    
    train_path = os.path.join(args.path, 'topic_{0}_train.jsonal'.format(
            args.name))
    #train_path="C:\\Users\\v-yiduoguo\\PycharmProjects\\pythonProject\\API_learning_2\\math\\topic_Algebra_train.jsonal"
    questions = []
    answers = []
    hints = []
    num = 0
    with open(train_path) as reader:
        for i, line in enumerate(reader):
            num += 1
            js = json.loads(line.strip())
            question = js["Question"]
            questions.append(question)
            answers.append(js["Label"])
            hints.append(js["Hint"])
    train_questions = questions#[test_num:]
    train_labels = answers#[test_num:]
    train_hints = hints#[test_num:]
    test_path = os.path.join(args.path, 'topic_{0}_test.jsonal'.format(
        args.name))
    questions = []
    answers = []
    num = 0
    with open(test_path) as reader:
        for i, line in enumerate(reader):
            num += 1
            js = json.loads(line.strip())
            question = js["Question"]
            questions.append(question)
            answers.append(js["Label"])
    test_questions = questions  # [test_num:]
    test_labels = answers  # [test_num:]


    return train_questions,train_labels,train_hints,test_questions,test_labels
    

def calculation_performance(results):
    num=0
    correct_num=0

    for ii in range(len(results)):
        num+=1
        if results[ii][0] != False:
            correct_num+=1
    return round(correct_num / (num) * 100, 2)

def get_triples(questions,math_prompt,labels,few_prompt=None):
        triples=[]
        for tt in range(len(questions)):
            triple=[]
            triple.append(questions[tt])
            triple.append(math_prompt)
            triple.append(labels[tt])
            if few_prompt is not None:
                triple.append(few_prompt)
            triples.append(triple)

        return triples
def get_wrong_group(wrong_triples,task_general_solutions,T=5):
    wrong_groups=[]
    if len(wrong_triples)<3:
        wrong_group=[]
        for ind in range(len(wrong_triples)):
            wrong_group.append(wrong_triples[ind])
        wrong_group.append(task_general_solutions)
        wrong_groups.append(wrong_group)
    else:
        for _ in range(T):
            idx=np.random.choice(np.arange(len(wrong_triples)),3)
            wrong_group=[]
            for ind in range(3):
                wrong_group.append(wrong_triples[idx[ind]])
            wrong_group.append(task_general_solutions)
            wrong_groups.append(wrong_group)
    return wrong_groups
def parse_solution(reason):
    Suggestions=[]
    ii=2
    while reason.find('Solution {0}'.format(ii))>0:
            ii += 1
            index = reason.find('Solution {0}'.format(ii))
            Suggestions.append(reason[:index])
            reason=reason[index:]
    return Suggestions
def extract_answer(answer_2,label):
    index = answer_2.find('answer')
    if index >= 0:
        Answer_Texts = answer_2[index:]
    else:
        Answer_Texts = answer_2
    index = Answer_Texts.find('is')
    if index >= 0:
        Answer_Texts = Answer_Texts[index + 3:]
    #   pdb.set_trace()
    index1 = Answer_Texts.find('boxed{')
    index2 = Answer_Texts.find('boxed')
    if index1 >= 0:
        index3 = Answer_Texts.rfind('}')
        Answer_Texts = Answer_Texts[index1 + 6:index3]
    elif index2 >= 0:
        index3 = Answer_Texts.rfind('.')
        Answer_Texts = Answer_Texts[index2 + 5:index3]
    #move un-related symbols
    Answer_Texts = Answer_Texts.replace('$', '')
    Answer_Texts = Answer_Texts.replace('%', '')
    Answer_Texts = Answer_Texts.replace(',', '')
    if len(Answer_Texts) > 0:
        if '.' == Answer_Texts[-1]:
            Answer_Texts = Answer_Texts[:-1]
    Answer_Texts = Answer_Texts.replace(' ', '')
    #make 'dfrac'='frac'
    if label.find('dfrac') >= 0:
        if Answer_Texts.find('dfrac') < 0:
            if Answer_Texts.find('frac') >= 0:
                Answer_Texts = Answer_Texts.replace('frac', 'dfrac')
    if Answer_Texts.rfind('=') > 0:
        Answer_Texts = Answer_Texts[Answer_Texts.rfind('=') + 1:]
    #1.00 is not equal to 1 problem
    try:
        if float(int(float(Answer_Texts))) - float(Answer_Texts) == 0:
            Answer_Texts = str(int(float(Answer_Texts)))
    except:
        Answer_Texts = Answer_Texts
    #make -{a}/{b}={-a}/{b}
    def move_reduce_sign(text):
        index=text.find('-')
        if index>=0:
            return '-'+text[:index]+text[index+1:]
        else:
            return text
    def find_nominator(text):
        index=text.find('{')
        index2=text.find('}')
        return text[index+1:index2]
    def find_denominator(text):
        index=text.rfind('{')
        index2=text.rfind('}')
        return text[index+1:index2]

    if 'frac' in Answer_Texts:
        Answer_Texts=move_reduce_sign(Answer_Texts)
        label=move_reduce_sign(label)
    # a cdot b -> ab
    if label.find('cdot')>=0:
        if Answer_Texts.find('cdot')<0:
            label=label.replace('\\cdot','')
    answer_state = True

    if Answer_Texts != label:
        answer_state = False
    # solving {a*b}/{a*c}!={b}/{c} question by turn the fraction into decimal.
    if label.find('\\dfrac')==0:
        try:
            label_float = float(find_nominator(label)) / float(find_denominator(label))
        except:
            label_float = 'Label can not convert to decimal'
        if Answer_Texts.find('\\dfrac')==0:
            try:
                answer_float = float(find_nominator(Answer_Texts)) / float(find_denominator(Answer_Texts))
            except:
                answer_float = 'Answer can not convert to decimal'
        else:
            try:
                #exec('answer_float=Answer_Texts')
                answer_float=float(Answer_Texts)
            except:
                answer_float='Answer can not convert to decimal'

        if answer_float==label_float:
                answer_state=True
    if Answer_Texts.find('\\dfrac')==0:
        try:
            answer_float = float(find_nominator(Answer_Texts)) / float(find_denominator(Answer_Texts))
        except:
            answer_float = 'Answer can not convert to decimal'
        if label.find('\\dfrac')==0:
            try:
                label_float=float(find_nominator(label))/float(find_denominator(label))
            except:
                label_float='Label can not convert to decimal'
        else:
            try:
                label_float = float(label)
            except:
                label_float = 'Label can not convert to decimal'
        if answer_float==label_float:
                answer_state=True
    return answer_state, Answer_Texts