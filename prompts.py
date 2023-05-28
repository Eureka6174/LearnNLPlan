# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
import numpy as np
def generation_solution_prompt(query):
    text = ''
    for ii in range(len(query)-1):
        text = add_wrong_case(text, query[ii])
    math_prompt = query[-1]
    text += """\n\n You can generate two or three new correct solutions to avoid the above wrong outputs and to solve all questions similar to the above questions. You must generate solutions different to those in the previous solutions: {0}? You can generate equations and python algorithms. When generating one solution, you should write no more than two sentences for one solution. You must not generate detailed examples as their are general solutions.""".format(
        math_prompt)
    text += """\n\nSolution 1: When calculating """
    return text

def compress_prompt(query):
    Solutions=query
    prompt = "You should summarize the similar solutions in {0} into one solution. You should maintain solutions for solving different situations. You must only output no more than five main solutions. When generating one solution, you should write no more than two sentences for one solution.\n\n".format(
        Solutions)
    return prompt

def few_shot_prompt(train_questions,train_labels,train_hints,examples_num=4):
    few_shot_prompt = """Here are the answers for the problems in the exam."""
    for example_id in range(examples_num):
        idx=np.random.permutation(len(train_questions))[0]
        hints=''
        for hint in range(len(train_hints[idx])):
            hints += train_hints[idx][hint]#train_hints[0][yy]
        few_shot_prompt +="""\n\nProblem {0}:{1}\n\nExplanation for Problem {0}:{2}\n\nThe answer is therefore {3}. \n""".format(example_id,train_questions[idx],hints,train_labels[idx])

    few_shot_prompt+="""\nProblem {0}:""".format(examples_num+1)
    return few_shot_prompt

def few_shot_prompt_add_data(few_shot_prompt,query,examples_num=4):
    question = query[0]
    prompt_and_program = query[1]
  #  prompt="<|im_start|>system\nYou are a helpful assistant.\n<|im_end|>\n<|im_start|>user\nHello!\n<|im_end|>\n<|im_start|>assistant\nHow can I help you?\n<|im_end|>\n<|im_start|>user\n{0}\n<|im_end|>\n<|im_start|>assistant\n".format(
    prompt=(few_shot_prompt + '\n' + question + '\n' + prompt_and_program + "\nExplanation for Problem {0}:".format(examples_num+1))
    return prompt


def inference_prompt(query):
    question = query[0]
    prompt_and_program = query[1]
    prompt = ("Question:" + question + "A:" + prompt_and_program)
    return prompt
def extract_prompt(question,answer):
    return "Give you a question, let's think step by step and then must output the result as 'the answer is \boxed{}." + "Question:" + \
               question + "A: Let's think step by step." + answer + 'Therefore, the answer is:'

def add_wrong_case(text,query):
    text+="\n\nQuestion:{0}\nwrong solution:{1}\nthe wrong answer:{2}\nthe correct answer is {3}".format(query[0],
                                                                                                   query[1],
                                                                                                   query[2],
                                                                                                  query[3])
    return text