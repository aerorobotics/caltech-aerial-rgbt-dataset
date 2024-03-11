#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import sys

import shutil

print("All packages imported!\n")

# Directory to search

root_directory = os.path.join(os.getcwd(),'data') 
root_directory = '/data'

# Remove uncompressed files after zipping
remove_after_unzipping = True

# Find all available bags
zip_files = sorted(glob.glob(os.path.join(root_directory, '**/*.zip'), recursive=True))

# Exit if no bags found
if (len(zip_files) == 0) :
    print("\nNo zip files found in",root_directory,"\n")
    sys.exit()

# De-compress all the located bags
ii = 0

for zip_file in zip_files :

    ii = ii+1

    cmd = ''
    print('({:3d}/{:3d}) >> {}'.format(ii, len(zip_files), zip_file))

    # Extract zip file
    extract_path = os.path.splitext(zip_file)[0]  # Use the same name as the zip file without the extension
    shutil.unpack_archive(zip_file, extract_path)

    # Remove zip file if requested
    if remove_after_unzipping :
        os.remove(zip_file)

# All done
print("\nDone!")
