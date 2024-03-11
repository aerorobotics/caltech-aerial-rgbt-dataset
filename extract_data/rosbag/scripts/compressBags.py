#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import sys
import subprocess

print("All packages imported!\n")

# Directory to search

root_directory = os.path.join(os.getcwd(),'data') 
root_directory = '/data'

BAGFILE_FORMAT = "**/*.bag"

COMPRESS_COMMAND = "rosbag compress --lz4 -f"

# Find all available bags
bags = sorted(glob.glob(os.path.join(root_directory,BAGFILE_FORMAT), recursive=True))

# Exit if no bags found
if (len(bags) == 0) :
    print("\nNo bags found in",root_directory,"\n")
    sys.exit()

# Compress all the located bags
ii = 0

for bag in bags:
    ii = ii+1

    print('({:3d}/{:3d}) >> '.format(ii, len(bags)),end='')
    bag_needs_compressing = True

    # Check to see if bag is compressed
    output = subprocess.check_output(f"rosbag info {bag}", shell=True, text=True)
    lines = output.split('\n')
    for line in lines:
        if "compression" in line and "none" not in line:
            print(f"{bag} already compressed, skipping")
            bag_needs_compressing = False
            break

    if bag_needs_compressing :

        # Form the compression command
        cmd = COMPRESS_COMMAND + " " + bag
        # print("\n---------------------------------------\n")
        print(f'{cmd}')
        
        # Compress the bag
        os.system(cmd)
        
        # Remove the original bag
        # os.remove(bag[:-4]+'.orig.bag')
        # Rename the orginal bag so it doesn't get processed
        os.rename(bag[:-4]+'.orig.bag', bag[:-4]+".old")

# All done
print("\nDone!")
