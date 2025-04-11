   #!/usr/bin/env python
import zstandard
import configparser
import io
import re
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
    now = str(datetime.datetime.now())
    return now

# Logging function
def log(log_file, content):
    with open(log_file, 'a') as file:
         time = str(tds()+"\t")
         content = str(content) + "\n"
         file.write(str(time + content))

# validate the zst file isn't corrupted
def check_zst_header(filename):
    with open(filename, 'rb') as f:
        magic_number = f.read(4)  # Read the first 4 bytes (magic number)
        if magic_number == b"\x28\xB5\x2F\xFD":
            valid_zstd_header = "true"
            message = "The zst bucket_path=" +filename + "is zst_valid = " + valid_zstd_header
            log(log_file, message)
        else:
            valid_zstd_header = "false"
            message = "The zst bucket_path=" +filename + "is NOT zst_valid = " + valid_zstd_header
            log(log_file, message)
        return valid_zstd_header

# get the source_dir and bucket IDs
def assign_vars(itemstr):
    itemstr = itemstr.split(",")
    for x in itemstr:
        if '/mnt/frozen_buckets' in x:
            source_dir = str(x).strip("[]'' ")   
            log(log_file,str("source_dir=" + source_dir))
        elif 'db_' in x:
            bucket_id = str(x).strip("[]'' ")
            log(log_file,str("bucket_id=" + bucket_id))
            return source_dir, bucket_id

def search_zst(err,enc,filename):
    fh = open(filename,'rb')
    dctx = zstandard.ZstdDecompressor()
    stream_reader = dctx.stream_reader(fh,read_size=4096)         
    text_stream = io.TextIOWrapper(stream_reader, encoding=str(enc), newline='\n', errors=str(err))
    first_x_bytes = text_stream.readlines(4096)
    #first_x_bytes = str(first_x_bytes)
    for x in first_x_bytes:
        #print()
        log(log_file,"DEBUG >>>" + str(x))
        meta_events = re.search(".host::(.{1,50})source::(.{1,50})sourcetype::(.{1,50}).[A-Z]",x)
        meta_ips  = re.search("\s(\d{2,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s",x)
        if meta_events is not None:
           bucket_host = str(meta_events.group(1))
           bucket_source = str(meta_events.group(2))
           bucket_sourcetype = str(meta_events.group(3))   
           message = ("bucket_path="+filename+ " bucket_host=" +bucket_host+ " bucket_source=" +bucket_source+ " bucket_sourcetype=" +bucket_sourcetype)
           log(log_file,message)
        if meta_ips is not None:          
            bucket_ips = str(meta_ips.group(1))
            message = ("bucket_path="+filename+" bucket_ips=" +bucket_ips)
            log(log_file,message)


if __name__ == "__main__":
    
    # Read the local config                                                  
    config = configparser.ConfigParser()
    config.read('gofishing.conf')          

    # Accessing values
    err = config.get('config', 'err')
    enc = config.get('config', 'enc')
    redis_host = config.get('config', 'redis_host')
    queue_name = config.get('config', 'workqueue')
    log_file = config.get('config', 'log_file')
    q = workqueue(name=queue_name, host=redis_host)
    
    while not q.empty():
          item = q.lease(lease_secs=10, block=True, timeout=2)
          if item is not None:
             itemstr = item.decode("utf-8")
             source_dir, bucket_id = assign_vars(itemstr)
             log(log_file,str("src_path=" + source_dir))
             log(log_file,str("bucket_id=" + bucket_id))
             journal_file = source_dir+"/rawdata/journal.zst"
             #set the journal_file
             log(log_file,"start analyzing bucket_path=" + journal_file)
             #check the zst headers
             check_zst_header(journal_file)
             #pull out the first X bytes with the err and enc fields set in the gofishing.conf
             search_zst(err,enc,journal_file)
             #apply regex function and reurn the bucket meta info and ips found                         
             log(log_file,"end analyzing bucket_path=" + journal_file)
             #finish queue
             q.complete(item)             