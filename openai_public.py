import openai
import backoff
import os
import json
from multiprocessing.pool import ThreadPool
import threading
# @backoff.on_exception(backoff.expo, openai.error.RateLimitError)
# def running_with_backoff(func, **kwargs):
#     return func(**kwargs)
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"
#put your API key here likes 'name':'key number'
API_dic = {'yaobo': 'c1dc6a15023d466aa66afcf1c2fdcbb2',}
default_engine = None
API_name_key_list = list(API_dic.items())


API_ID=0
lock = threading.Lock()
def set_next_API_ID():
    global API_ID
    lock.acquire()
   # print("API_ID", API_ID)
    API_ID = (API_ID + 1) % len(API_name_key_list)
    openai.api_base = "https://{0}.openai.azure.com/".format(API_name_key_list[API_ID][0])
    openai.api_key = API_name_key_list[API_ID][1]
    lock.release()
set_next_API_ID()
def multi_threading_running(func, queries, n=40, multiple_API=True):
    @backoff.on_exception(backoff.expo, openai.error.RateLimitError)
    @backoff.on_exception(backoff.expo, openai.error.APIError)
    @backoff.on_exception(backoff.expo, openai.error.APIConnectionError)
    def wrapped_function(query):
        if multiple_API:
            set_next_API_ID()
        return func(query)

    pool = ThreadPool(n)
    replies = pool.map(wrapped_function, queries)
    return replies

def query_azure_openai_chatgpt_chat(query,temperature=0.0):
    #try:
    response = openai.ChatCompletion.create(
                engine="gpt-35-turbo",  # The deployment name you chose when you deployed the ChatGPT or GPT-4 model.
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": query},
                ],
                temperature=temperature,
                max_tokens=2000,
            )
    try:
        return response['choices'][0]['message']['content']
    except:
        return ' '


def query_azure_openai_chatgpt_complete(query,temperature=0.0):
    #print('text3')
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=query,
        max_tokens=2000,
        temperature=temperature,
        stop=["<END>"])

    return response["choices"][0]["text"]