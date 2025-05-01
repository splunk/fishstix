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
Run the fishstix_opt/**install_fishstix.sh** script to start the FishStix Installer
This will run bin/setup/_install_reqs.sh_ and install all pre-requisite components listed
  - apt install nano
  - apt install docker.io
  - apt install redis-server
  - apt install redis-tools
  - pip install redis splunklib splunk-sdk
  - Install Microk8s v 1.32 & logout
- Logout and back into the host
Continue the installation by logging back in and running the **install_fishstix.sh** again to complete setup
  - runs the _setup_fishstix.sh_ script to
      - deploy all files to the **/opt/fishstix** directory
      - Patch file search_command.py to address bug with the splunk-sdk  (https://github.com/splunk/splunk-sdk-python/issues/605)
      - Install the provided fishstix.spl file for the FishStix UI
  - runs the _finish_config.sh_ script to prompt the installer for completing the Redis config changes to:
      - /etc/redis/redis.conf
      - /opt/fishstix/fxcopier.conf
      - /opt/fishstix/fxrestore.conf
      - Restart Redis & ensure it's listening on the IP that was set
    
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

