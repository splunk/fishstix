#!/usr/bin/env python
import zstandard
import io
import re
import sys
import redis
import uuid
import hashlib
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

def check_zst_header(filename):
    with open(filename, 'rb') as f:
        magic_number = f.read(4)  # Read the first 4 bytes (magic number)
        if magic_number == b"\x28\xB5\x2F\xFD":
            valid_zstd_header = "true"
            message = "The zst is valid = " + valid_zstd_header
            log(log_file, message)
        else:
            valid_zstd_header = "false"
            message = "The zst is NOT valid" + valid_zstd_header
            log(log_file, message)
        # Read the first 15 bytes to inspect additional header information
        header_data = f.read(15)
        header_hex = (header_data.hex())
        return valid_zstd_header, header_hex

def assign_vars(itemstr):
    itemstr = itemstr.split(",")
    for x in itemstr:
        if '/mnt' in x:
            source_dir = str(x).strip("[]'' ")
            log(log_file,str("Source Directory: " + source_dir))
        elif 'db_' in x:
            bucket_id = str(x).strip("[]'' ")
            log(log_file,str("Bucket Id:" + bucket_id))
        elif "restored" in x:
            restored_index_name = str(x).strip("[]'' ")
            message = ("Destination Index: " + restored_index_name)
            destination_dir = "/mnt/data/" + restored_index_name +"/thaweddb/" + bucket_id
            message2 =("Destination Directory:" + destination_dir)
            log(log_file, message)
            log(log_file, message2)
            return source_dir, bucket_id, restored_index_name


def search_zst_beginning(err,filename):
    enc = ["utf_8"]
    for y in enc:
        fh = open(filename,'rb')
        dctx = zstandard.ZstdDecompressor()
        stream_reader = dctx.stream_reader(fh,read_size=4096) 
        text_stream = io.TextIOWrapper(stream_reader, encoding=str(y), newline='\n', errors=str(err))
        first_x_bytes = text_stream.readlines(2048)
        for x in first_x_bytes:
            printable = x.isprintable()
            log(log_file, str("DEBUG encoding_option="+str(y)+" errors="+str(err)+"  "+str(x)))
            r  = re.search("host::(.{1,50})source::(.{1,50})sourcetype::(.{1,50})",x)
            if r is not None:
               host = str(r.group(1))
               source = str(r.group(2))
               sourcetype = str(r.group(3))
               message = ("bucket_path="+filename+ " bucket_host=" +host+ " bucket_source=" +source+ " bucket_sourcetype=" +sourcetype)
               log(log_file, message) 
            else:
               pass


if __name__ == "__main__":
     err = ["ignore"]
     log_file="/opt/fishstix/logs/gofishing.log"  
     q = workqueue(name="fishingqueue", host=sys.argv[1])
     message1 = str("Worker with sessionID: " +  q.sessionID())
     log(log_file,message1)
     message2 = str("Initial queue state: empty=" + str(q.empty()))
     log(log_file,message2)


     while not q.empty():
         item = q.lease(lease_secs=10, block=True, timeout=2) 
         if item is not None:
             itemstr = item.decode("utf-8")
             source_dir, bucket_id, restored_index_name = assign_vars(itemstr)
             journal_file = source_dir+"/rawdata/journal.zst"
             check_zst_header(journal_file)
             for x in err:
                 search_zst_beginning(x,journal_file) 
             q.complete(item)
