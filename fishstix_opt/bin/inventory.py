#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 15:37:45 2025

@author: klawrencegupta
"""

import os
import re
from pathlib import Path

def find_files_recursively_pathlib(target_directory, search_name):
    root = Path(target_directory)
    found_files = list(root.rglob(search_name))
    return found_files

def get_fsize(filename):
    file_size = os.path.getsize(filename)
    return file_size


if __name__ == "__main__":
    print("Mount your frozen buckets to /mnt/frozen_buckets and run this script > .csv to create a new inventory file"
    print("absolute_path,file_size_bytes,bucket_id")
    target_directory = "/mnt/frozen_buckets"
    file_to_find = "journal.zst"
    #print(target_directory) //DEBUG
    #print(file_to_find) //DEBUG
    found_files = find_files_recursively_pathlib(target_directory, file_to_find)
    for filename in found_files:
        #print(filename) //DEBUG
        r  = re.search("(db_\d+.\d+.\d+)",str(filename))
        if r is not None:
           bucket_id = str(r.group(1))
           file_size = str(get_fsize(filename))
           print(str(filename) +"," + file_size + "," +bucket_id)
        else:
           print(f"\nNo files found in directory '{target_directory}'.")
