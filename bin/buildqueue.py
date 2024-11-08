import csv
import redis
import os
import datetime



# Replace with your Redis server details
host = "10.202.13.180"
port = 6379
copy_list_key = "copyqueue"
restore_list_key = "restorequeue"
#fishing_list_key = "fishingqueue"

# Connect to Redis
redis_client = redis.Redis(host=host, port=port)

#Files
file_path = "/opt/splunk/etc/apps/fishstix/lookups/restorequeue.csv"
#fish_path = "/opt/splunk/etc/apps/fishstix/lookups/fishingqueue.csv"
log_file = "/mnt/data/buildqueue.log"

# Time Date stamper
def tds():
    now = str(datetime.datetime.now())
    return now

def log(log_file, content):
  with open(log_file, 'a') as file:
      time = str(tds()+"\t")
      content = content + "\n"
      file.write(str(time + content))


with open(file_path, "r") as csvfile:
    reader = csv.reader(csvfile)
    # Skip header row (optional)
    next(reader, None)
    # Loop through each row in the CSV
    for row in reader:
        # Add each row as a single element to the Redis list
        redis_client.rpush(copy_list_key, ",".join(row))
        redis_client.rpush(restore_list_key, ",".join(row))
        log(log_file,str("Copy & Restore queues are now prepped"))

#with open(fish_path, "r") as fishfile:
#    reader = csv.reader(fishfile)
    # Skip header row (optional)
#    next(reader, None)
    # Loop through each row in the CSV
#    for row in reader:
        # Add each row as a single element to the Redis list
#        redis_client.rpush(fishing_list_key, ",".join(row))
#        log(log_file,str("The Fishing queue are now prepped"))

