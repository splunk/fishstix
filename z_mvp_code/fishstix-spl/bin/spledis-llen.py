#!/usr/bin/env python

import os
import redis
import datetime
import sys
import configparser
import splunklib


#Read
config = configparser.ConfigParser()
config.read('../default/spledis.conf')
# Accessing values
host = config.get('config', 'host')
port = config.get('config', 'port')


# Connect to Redis
redis_client = redis.Redis(host=host, port=port)
log_file="../logs/buildqueue.log"
queue_name = sys.argv[1]
#print(host)
#print(port)
#print(queue_name)


# Time Date stamper
def tds():
    now = str(datetime.datetime.now())
    return now

def log(log_file, content):
    with open(log_file, 'a') as file:
         time = str(tds()+"\t")
         content = str(content) + "\n"
         file.write(str(time + content))

def rpush(queue_name, record):
     redis_client.rpush(queue_name,str(record))
     message = "redis_queue:" + str(queue_name) + "record:" + str(record)
     log(log_file,message)

def llen(queue_name):
     q_counter = redis_client.llen(queue_name)
     message = "redis_queue:" + str(queue_name) + "q_counter:" + str(q_counter)
     log(log_file,message)

def lrange(queue_name):
     q_list = redis_client.lrange(queue_name,"0","-1")
     message = "redis_queue:" + str(queue_name) + "q_list:" + str(q_list)
     log(log_file,message)


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration

@Configuration()
class StreamingSpledis(StreamingCommand):

    def stream(self, events):
        for event in events:            
            value = llen((queue_name,str(value))
            log(log_file,str(value))
            yield event

dispatch(StreamingSpledis, sys.argv, sys.stdin, sys.stdout, __name__)
