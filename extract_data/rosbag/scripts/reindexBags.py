#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import sys

print("All packages imported!\n")

# Directory to search
root_directory = os.path.join(os.getcwd(),'data') 
root_directory = '/data'

# Commands and formats
BAGFILE_FORMAT = "**/*.bag.active"
REINDEX_COMMAND = "rosbag reindex -f"

# Print script purpose
str = "Reindexing active rosbags in "+root_directory
print("\n\n")
print('=' * len(str))
print(str)
print('=' * len(str))
print("\n\n")

# Find all available bags
bags = sorted(glob.glob(os.path.join(root_directory,BAGFILE_FORMAT), recursive=True))

# Exit if no bags found
if (len(bags) == 0) :
    print(f"\nNo {BAGFILE_FORMAT} files found in",root_directory,"\n")
    sys.exit()

# Compress all the located bags
ii = 0

for bag in bags:
    ii = ii+1

    # Form the reindex command
    cmd = REINDEX_COMMAND + " " + bag
    print("\n---------------------------------------\n")
    print('({:3d}/{:3d}) >> {}'.format(ii, len(bags), cmd))
    
    # Re-index the bag
    os.system(cmd)
    
    # Remove the 'active' tag from the file name
    os.rename(bag, bag.replace(".active", ""))

    # Remove the old bag, un-indexed bag
    os.remove(bag.replace(".active", ".orig.active"))

# All done
print("\nDone!")
