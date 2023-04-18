# Project

This project introduces the Learning to Program (LP) method, which aims to learn task programs in text form from the training set using Large Language Models (LLMs) themselves. The method then uses the learned program to guide LLMs to solve complex tasks. Our method only requires access to LLMs and does not need to update their parameters. Unlike previous self-critiquing methods, this method attempts to improve task performance by learning task programs from the training datapoints provided by humans. It also allows LLMs to learn and utilize new knowledge from the training set. Also, we hope that our new learning diagram can inspire the research community to investigate learning algorithms based on natural language. The learned task experience in this kind of learning algorithm is written in natural language, making it understandable to humans. Additionally, the learned content may provide insights into understanding the behavior of LLMs. This project is still a work in progress.


# Requirements
please install these packages first.
```
pip install openai
pip install numpy
pip install backoff
```
Then put your openai API in the api_dict of the openai_public.py file (Line 13).
# Training
We provide 10 tasks from the AMPS dataset here (paper: Measuring Mathematical Problem Solving With the MATH Dataset). You can find the details of the tasks in Table 1 of our paper (Learning to program with natural language). 
```
python learning_to_program.py --name 1 #task id --model #LLMs --path xxx #the file path
                              --epoch 10 --batch_size 32 --valid_size 3 #the validation set is equal to valid_size*batch_size 
                              --T 5 #the number of revision candidates --threshold 1.0 --few False #whether activate the few-shot CoT setting 
```
# Checking the learned task program
During the training process, the validation performance, test performance and current task program would be printed.

After the training process, you can check the learned task program in the file: khan_topic_{task_id}.npy. 
