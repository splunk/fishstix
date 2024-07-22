import csv
import redis

# Replace with your Redis server details
host = "ip"
port = 6379
list_key = "restorequeue"

# Connect to Redis
redis_client = redis.Redis(host=host, port=port)

# Open the CSV file
with open("/opt/splunk/etc/apps/fishstix/lookups/restorequeue.csv", "r") as csvfile:
    reader = csv.reader(csvfile)

    # Skip header row (optional)
    next(reader, None)

    # Loop through each row in the CSV
    for row in reader:
        # Add each row as a single element to the Redis list
        redis_client.rpush(list_key, ",".join(row))

print(f"Data loaded into Redis list: {list_key}")