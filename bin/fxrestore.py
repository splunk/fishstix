#!/usr/bin/env python

# Based on http://peter-hoffmann.com/2012/python-simple-queue-redis-queue.html 
# and the suggestion in the redis documentation for RPOPLPUSH, at 
# http://redis.io/commands/rpoplpush, which suggests how to implement a work-queue.

 
import redis
import uuid
import hashlib
import os
import sys
import subprocess
import datetime


class workqueue(object):
    """Simple Finite Work Queue with Redis Backend

    This work queue is finite: as long as no more work is added
    after workers start, the workers can detect when the queue
    is completely empty.

    The items in the work queue are assumed to have unique values.

    This object is not intended to be used by multiple threads
    concurrently.
    """
    def __init__(self, name, **redis_kwargs):
       """The default connection parameters are: host='localhost', port=6379, db=0

       The work queue is identified by "name".  The library may create other
       keys with "name" as a prefix. 
       """
       self._db = redis.StrictRedis(**redis_kwargs)
       # The session ID will uniquely identify this "worker".
       self._session = str(uuid.uuid4())
       # Work queue is implemented as two queues: main, and processing.
       # Work is initially in main, and moved to processing when a client picks it up.
       self._main_q_key = name
       self._processing_q_key = name + ":processing"
       self._lease_key_prefix = name + ":leased_by_session:"

    def sessionID(self):
        """Return the ID for this session."""
        return self._session

    def _main_qsize(self):
        """Return the size of the main queue."""
        return self._db.llen(self._main_q_key)

    def _processing_qsize(self):
        """Return the size of the main queue."""
        return self._db.llen(self._processing_q_key)

    def empty(self):
        """Return True if the queue is empty, including work being done, False otherwise.

        False does not necessarily mean that there is work available to work on right now,
        """
        return self._main_qsize() == 0 and self._processing_qsize() == 0

# TODO: implement this
#    def check_expired_leases(self):
#        """Return to the work queueReturn True if the queue is empty, False otherwise."""
#        # Processing list should not be _too_ long since it is approximately as long
#        # as the number of active and recently active workers.
#        processing = self._db.lrange(self._processing_q_key, 0, -1)
#        for item in processing:
#          # If the lease key is not present for an item (it expired or was 
#          # never created because the client crashed before creating it)
#          # then move the item back to the main queue so others can work on it.
#          if not self._lease_exists(item):
#            TODO: transactionally move the key from processing queue to
#            to main queue, while detecting if a new lease is created
#            or if either queue is modified.

    def _itemkey(self, item):
        """Returns a string that uniquely identifies an item (bytes)."""
        return hashlib.sha224(item).hexdigest()

    def _lease_exists(self, item):
        """True if a lease on 'item' exists."""
        return self._db.exists(self._lease_key_prefix + self._itemkey(item))

    def lease(self, lease_secs=60, block=True, timeout=None):
        """Begin working on an item the work queue. 

        Lease the item for lease_secs.  After that time, other
        workers may consider this client to have crashed or stalled
        and pick up the item instead.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self._db.brpoplpush(self._main_q_key, self._processing_q_key, timeout=timeout)
        else:
            item = self._db.rpoplpush(self._main_q_key, self._processing_q_key)
        if item:
            # Record that we (this session id) are working on a key.  Expire that
            # note after the lease timeout.
            # Note: if we crash at this line of the program, then GC will see no lease
            # for this item a later return it to the main queue.
            itemkey = self._itemkey(item)
            self._db.setex(self._lease_key_prefix + itemkey, lease_secs, self._session)
        return item

    def complete(self, value):
        """Complete working on the item with 'value'.

        If the lease expired, the item may not have completed, and some
        other worker may have picked it up.  There is no indication
        of what happened.
        """
        self._db.lrem(self._processing_q_key, 0, value)
        # If we crash here, then the GC code will try to move the value, but it will
        # not be here, which is fine.  So this does not need to be a transaction.
        itemkey = self._itemkey(value)
        self._db.delete(self._lease_key_prefix + itemkey)

# Time Date stamper
def tds():
    now = str(datetime.datetime.now())
    return now

def log(log_file, content):
  with open(log_file, 'a') as file:
      time = str(tds()+"\t")
      content = content + "\n"
      file.write(str(time + content))


#Get environment vars for SPLUNK_HOME
def get_env():
    SPLUNK_HOME = os.environ.get("SPLUNK_HOME")
    if SPLUNK_HOME is None:
        SPLUNK_HOME = "/opt/splunk/"
    return SPLUNK_HOME


def assign_vars(itemstr):
    itemstr = itemstr.split(",")
    for x in itemstr:
        if '/mnt' in x:
            source_dir = str(x).strip("[]'' ")
            message1 = str("Source Directory: " + source_dir)
            log(log_file,message1)
        elif 'db_' in x:
            bucket_id = str(x).strip("[]'' ")
            message2 = str("Bucket Id:" + bucket_id)
            log(log_file,message2)
        elif "restored" in x:
            restored_index_name = str(x).strip("[]'' ")
            message3 = str("Destination Index: " + restored_index_name)
            log(log_file,message3)
            destination_dir = "/mnt/data/" + restored_index_name +"/thaweddb/" + bucket_id
            message4 = str("Destination Directory:" + destination_dir)
            log(log_file,message4)
            return source_dir, bucket_id, restored_index_name

#Generic command for shell
def run_command(cmd): 
    bufsize = 10240
    process = subprocess.check_output(cmd, shell=True,bufsize=bufsize)
    output = process.decode('utf-8').strip('\n')
    log(log_file,output)
    return output


if __name__ == "__main__":
    SPLUNK_HOME=get_env()
    host = "10.202.13.180"
    scriptpath = "/opt/fishstix/bin"
    sys.path.append(os.path.abspath(scriptpath))
    log_file = "/mnt/data/fxrestore.log"
    q = workqueue(name="restorequeue", host=host)
    message5 = str("Worker with sessionID: " +  q.sessionID())
    message6 = str("Initial queue state: empty=" + str(q.empty()))
    log(log_file,message5)
    log(log_file,message6)
    while not q.empty():
        item = q.lease(lease_secs=10, block=True, timeout=2) 
        if item is not None:
            itemstr = item.decode("utf-8")
            source_dir, bucket_id, restored_index_name = assign_vars(itemstr)
            command_tbr= "sudo "+ SPLUNK_HOME + "/bin/./splunk rebuild " + "/mnt/data/"+restored_index_name+"/thaweddb/"+bucket_id
            message7 = str(command_tbr)
            log(log_file,message7)
            run_command(command_tbr)  
            q.complete(item)
        else:
         log(log_file,str("Waiting for work"))
         log(log_file,str("Queue empty, exiting"))
