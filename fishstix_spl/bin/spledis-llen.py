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

def llen(queue_name):
     q_counter = redis_client.llen(queue_name)
     message = "redis_queue:" + str(queue_name) + "_counter:" + str(q_counter)
     log(log_file,message)
     print(message)


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration

@Configuration()
class StreamingSpledisllen(StreamingCommand):
    def stream(self, events):
        for event in events:
            for key in event:
                value = event[key]
                #log(log_file,str(key))
                if "redis" in key:
                    llen(queue_name)
            yield event

dispatch(StreamingSpledisllen, sys.argv, sys.stdin, sys.stdout, __name__)
