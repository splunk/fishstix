**3/14/2025 Kate Lawrence-Gupta
FishStix - a Splunk frozen data manager 
v 1.0.0**

Project Details - https://github.com/splunk/fishstix

Fishstix starts by using an inventory of the frozen data available in your environment. This inventory follows a simple CSV schema
FishStix requires the frozen buckets to be mounted to this host at /mnt/data/frozen_buckets/ for processing by the local container & Redis services.
Upload your CSV inventory to the index=fx and using the provided sourcetype=fx_inventory and this page will populate with the inventory details of your frozen data

CSV Schema:
local path to data,
  file_size_bytes,
    bucket_id,
      

Example:
/mnt/data/frozen_buckets/index4/db_1726679943_1726679518_418,10240,db_1726679943_1726679518_418

**Installer**
The setup runs in 4 steps:

- Clone this repo
- Run the bin/microk8s_installer.sh to setup Microk8s deployment
- Logout and back into the host
- Continue the installation by logging back in and using the bin/setup_fishstix.sh script for the final setup

**Components required**

**Splunk: version 9.4+**

**Microk8s/Docker:**
splunk/splunk:latest (Splunk + pip redis w/ fxrestore.py)
lokispundit/fxcopier:latest (Alpine + pip redis w/ fxcopier.py)
Dockerfile also provided


**Redis:**
redis-server, redis-cli & redis.py (pip)
spledis.py, spledis-llen.py (pip redis, splunklib)
* _bug splunklib (https://github.com/splunk/splunk-sdk-python/issues/605)
* workaround :
* replace the default /usr/local/lib/python3.10/dist-packages/splunklib/searchcommands/search_command.py 
file with the following search_command.py from the bin directory

def process():
...
self._process_protocol_v1 to **self._process_protocol_v2**  // this bug prevents chunked=true from being honored)


