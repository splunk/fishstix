#Kate Lawrence-Gupta - Splunk - Principal Platform Architect
#FishStix - restore script
#The FishStix UI creates a file in lookups named nifi_restore_list.csv the list of buckets to be restored
#the default index restored_data-100

#This script is just a wrapper for the ./splunk rebuild command to ruse a generated CSV file. The only fields required are the absolute_path
# of the frozen data (local mount required) and the bucket_ids to be rebuilt.

#Libraries
import os
import subprocess
import csv
import shutil


#Get environment vars for SPLUNK_HOME
def get_env():
    SPLUNK_HOME = os.environ.get("SPLUNK_HOME")
    if SPLUNK_HOME is None:
        SPLUNK_HOME = "/opt/splunk/"
    return SPLUNK_HOME

#Read the nifi_restore_list.csv for columns
def read_column(filename, col_index):
  with open(filename, 'r') as csvfile:
    reader = csv.reader(csvfile)
    column = []
    for row in reader:
      if col_index < len(row):
        column.append(row[col_index])
    return column

#Read the nifi_restore_list.csv for rows
def read_row(filename, row_index):
  with open(filename, 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row_num, row in enumerate(reader):
      if row_num == row_index:
        return row
    return None

#Requires Python 3.11 to use dirs_exist_ok as part of shutil.copytree command to ensure the subdirectory gets recursively copied to the thawed dir
def copy_directory_overwrite(source_dir, bucket_id, restored_index_name):
  destination_dir = SPLUNK_HOME + "var/lib/splunk/" + restored_index_name +"/thaweddb/" + bucket_id  
  print("Destination: " +destination_dir)
  if not os.path.exists(source_dir):
    raise RuntimeError(f"Source directory '{source_dir}' does not exist.")
  try:
    shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
  except OSError as e:
    raise OSError(f"Error copying '{source_dir}' to '{destination_dir}': {e}")

#Main Function

if __name__ == "__main__":
    #Default restore index
    restored_index_name = "restored_data-100"
    #get SPLUNK_HOME
    SPLUNK_HOME=get_env()
    #FishStix UI generated lookup file
    nifi_restore_list = SPLUNK_HOME+"/etc/apps/fishstix/lookups/restorequeue.csv"
  
    #absolute_path
    col_index_1 = 0  # 0-based index
    column_1 = read_column(nifi_restore_list, col_index_1)

    #bucket_ids
    col_index_2 = 1
    column_2= read_column(nifi_restore_list, col_index_2)

#Loop through the absolute_paths to gather the source_dir
    for x in column_1:
        if not "absolute_path" in x:
            source_dir = x
            print("Source: " + source_dir)
#Loop through the buckets to gather the bucket_ids
    for y in column_2:
        if not "bucket_id" in y:
            bucket_id = str(y)
            #copy buckets to restored_index_name/thaweddb directory
            copy_directory_overwrite(source_dir, bucket_id, restored_index_name)
            bufsize = 10240
            #Splunk rebuild command by bucket_id
            command_tbr= SPLUNK_HOME + "/bin/./splunk rebuild " + SPLUNK_HOME + "/var/lib/splunk/"+restored_index_name+"/thaweddb/"+bucket_id
            print(command_tbr)
            #run the command via subprocess
            process = subprocess.check_output(command_tbr, shell=True,bufsize=bufsize)
            output = process.decode('utf-8').strip('\n')


                

            
            