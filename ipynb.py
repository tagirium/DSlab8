#!/usr/bin/env python
# coding: utf-8

# In[2]:


from multiprocessing import Process, Pipe
from functools import partial
from time import sleep
import logging


# In[3]:


logging.basicConfig(level=logging.INFO, format='%(message)s')


# In[4]:


def event(process_name, vector):
    vector[process_name] += 1
    logging.info(f'Event has happened in followin process - {process_name}: {list(vector.values())}')
    return vector


# In[5]:


def send_message(pipe, process_name, vector):
    vector[process_name] += 1
    pipe.send(vector)
    logging.info(f'Message has been sent from following process - {process_name}: {list(vector.values())}')
    return vector


# In[6]:


def recv_message(pipe, process_name, vector):
    vector[process_name] += 1
    received_vector = pipe.recv()
    for p in vector:
        vector[p] = max(vector[p], received_vector[p])
    logging.info(f'Message has been received at following process - {process_name}: {list(vector.values())}')
    return vector


# In[7]:


def run_process(process_name, vector, actions):
    print(f'Process {process_name} is running')
    for action in actions:
        vector = action(vector)
        sleep(0.01)
    print(f'Process - {process_name}: {list(vector.values())}')


# In[8]:


if __name__ == '__main__':
    pipe_ab, pipe_ba = Pipe()
    pipe_bc, pipe_cb = Pipe()

    actions = {
        'a': 
            [partial(send_message, pipe_ab, 'a'),
            partial(send_message, pipe_ab, 'a'),
            partial(event, 'a'),
            partial(recv_message, pipe_ab, 'a'),
            partial(event, 'a'),
            partial(event, 'a'),
            partial(recv_message, pipe_ab, 'a'),],
        'b': 
            [partial(recv_message, pipe_ba, 'b'),
            partial(recv_message, pipe_ba, 'b'),
            partial(send_message, pipe_ba, 'b'),
            partial(recv_message, pipe_bc, 'b'),
            partial(event, 'b'),
            partial(send_message, pipe_ba, 'b'),
            partial(send_message, pipe_bc, 'b'),
            partial(send_message, pipe_bc, 'b'),],
        'c': 
            [partial(send_message, pipe_cb, 'c'),
            partial(recv_message, pipe_cb, 'c'),
            partial(event, 'c'),
            partial(recv_message, pipe_cb, 'c'),],
    }

    vector = {'a': 0, 'b': 0, 'c': 0}
    procs = []
    for process_name, action in actions.items():
        procs.append(Process(target=run_process, args=(process_name, vector, action)))
    for process in procs:
        process.start()
    for process in procs:
        process.join()




