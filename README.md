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
    bucket_id
      

Example:
/mnt/data/frozen_buckets/index4/db_1726679943_1726679518_418,10240,db_1726679943_1726679518_418

**Installer**
- Clone this repo
- run the provided **fx_install.py** and follow the prompts
    
**Microk8s/Docker:**
- splunk/splunk:latest (Splunk + pip redis w/ fxrestore.py)
- lokispundit/fxcopier:latest (Alpine + Python 3.11 to support shuttil recursive copy feature  + pip redis w/ fxcopier.py)
- Dockerfile also provided along with build.sh 

**Redis:**
- redis-server, redis-tools & redis (via pip)
- spledis.py, spledis-llen.py (pip redis, splunklib, splunk-sdk)

**spledis.py**
- There is a bug in the splunklib code /usr/local/lib/python3.10/dist-packages/splunklib/searchcommands/search_command.py that prevents chunked=true from working on custom python commands.
- patched search_command.py file provided

