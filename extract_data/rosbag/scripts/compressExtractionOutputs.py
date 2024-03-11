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
remove_after_zipping = True

# Find all available bags
abs_dirs = sorted(glob.glob(os.path.join(root_directory, '**/'), recursive=True))

# Exit if no bags found
if (len(abs_dirs) == 0) :
    print("\nNo subfolders found in",root_directory,"\n")
    sys.exit()

# Compress all the located bags
ii = 0

for bag_dir in abs_dirs :

    ii = ii+1

    # Get the folder name
    print("\n---------------------------------------\n")
    cmd = ''
    print('({:3d}/{:3d}) >> {}'.format(ii, len(abs_dirs), bag_dir))

    data_folders = ['csv',
                    'images',
                    'processed' ]

    for data_folder in data_folders :
        folder = os.path.join(bag_dir,data_folder)

        print(f'             {folder}',end='...')

        if os.path.exists(folder):
            # Compress folder
            shutil.make_archive(folder, 'zip', folder)
            print("done!")

            # Remove folder
            if (remove_after_zipping) :
                shutil.rmtree(folder)

        else:
            print(f"missing, skipping")


# All done
print("\nDone!")
