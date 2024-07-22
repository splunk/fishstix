**FishStix** - Lightweight NIFI-based Inventory of Splunk Frozen data from multiple sources 

**Background**
Frozen data is plentiful and sucks since it has no metadata. This makes organizing and finding what you need to restore very difficult.
While Splunk does keep track of freezing the bucket but not where it's going after that and not for long. 
This makes managing this data difficult and expensive.
 
**Issue**: 
An inventory of frozen data is needed to make this data usable. 
At a minimum we need to understand 
- the location of the frozen data 
- the original index and  
- then which specific bucket_ids to restore
- restoration_index

**Solution Proposal:**
NIFI creates a universal and lightweight strategy to allow us to continuously poll multiple locations (local|remote|s3) for metadata and using default NIFI attributes create an inventory of frozen data available.

Splunk extracts these fields from the NIFI attributes and gives us
-  bucket_full_path,bucket_relative_path,zst_file,owner,ts_1,ts_2,ts_3, group,bucket_size_bytes,bucket_perms,nifi_guid
  

With the FishStix UI/SPL we filter what data is needed by index_name. A lookup file is then created with a list of buckets that are needed for the restore ; the restore.py script is then run against only the specific buckets listed and the data is put in net new index. There are 3 staging indexes included called restored_data-100/200/300.

**NIFI Topology**

**Basic**
- List Objects >> route ALL attributes to CSV >> local Splunk TCP/9995 
- the full attribute list also gives us the file_size_bytes, owner, group and permissions data as well
- **sourcetype = fx_inventory_data**

**Restore Process - Basic**

Using the FishStix UI create a list of buckets to be restored and put data into the lookup **restorequeue.csv**

- Use the bin/restore.py to restore the list of buckets for restoration.
- This restore script requires python 3.11.5+ due to a known issue with shutil recursive copy that is resolved at this minimum version
- This restore script will kick of a
  - recursive copy of files from their source directory to the staged directory for restoration
  - a serial restore of the buckets rovided in the restorequeue.csv to the staged restored_data_100 index which is already searchable
- Data is searchable in **index=restored_data_100**

**Restore Process - Advanced**
Use the fx_advanced_build.sh script to install/configure the following additional components:
- Redis 5.0.7+
- Microk8s 1.2.9+ and enable storage & DNS
- buildqueue.py
- fxcopier.py
- fxrestore.py

Using the FishStix UI create a list of buckets to be restored and put data into the lookup **restorequeue.csv**

- Use the _buildqueue.py_ script to copy the data from the CSV file to 2 REDIS queues (copyqueue & restorequeue)
- Deploy the _fxcopier.yaml_ (kubectl apply -f) to recursively copy the files from their source to their destination in the staged index
 - The fxcopier Pod runs the fxcopier.py code on an Alpine Linux + Python 3.11.9 w/ shutil & REDIS
 - The _fxcopier.py_ reads from the REDIS-copyqueue and uses shutil to copy the needed files it then removes items from the queue once they've been sucessfully copied

Deploy the _fxrestore.yaml_ (kubectl apply -f) to spin up Splunk HF containers to run the following code 

pip install redis; python /opt/splunk/etc/apps/fishstix/bin/fxrestore.py

 - The _fxrestore.py_ will read from the REDIS-restorequeue and begin the restore/thawing process on a per bucket basis.
 - This process is asynchonous and can be run in parallel since it's queue-based and each replica will run as a subscriber to the queue
- Data is searchable in index=restored_data_100

**Testing perforamnce:**
- I was able to restore 10 buckets of data that would have taken ~2000 seconds to restore serially down to ~780 seconds to run with just 2 replicas
- More recent testing I was able to restore 20 buckets in parallel and have 22GB searchable in ~30 minutes using just 5 replicas


**Known Issues:**
- [ ] requires 3.11.5+
- [ ] fxrestore POD is not automatically deploying needed code & logging is incorrect
- [ ] Splunk TCP input is lazy and should be moved to HEC
- [ ] The frozen index name must be in the absolute_path name

