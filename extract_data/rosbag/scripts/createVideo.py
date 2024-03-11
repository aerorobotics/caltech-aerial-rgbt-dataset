#!/usr/bin/env python3

# General imports
import os
import re
import glob
import shutil
import csv
import math
import numpy as np
import cv2
from numpy.lib.function_base import percentile

import argparse

# Inputs
root_directory = os.path.join(os.getcwd(),'data')
root_directory = '/data'

percentile_lo = 10   # Depth lower cutoff [10]
percentile_hi = 90  # Depth upper cutoff [90]

payload_inverted = 1

# Leave empty to skip (make black)

# Video frame
img_array = np.empty([1,3], dtype=object)

img_array[0][0] = '_eo_color_image_color_compressed.csv'
img_array[0][1] = '_boson_thermal_image_raw.csv'
img_array[0][2] = '_eo_mono_image_mono_compressed.csv'

img_array_ref = (0,1)  # Index of timing reference image

#----------------------

# If we have an arg, override the root_directory variable
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', type=str, default=root_directory, help='Path to rosbag files')
args = parser.parse_args()
root_directory = args.path

# Find all the bag files in the directory
bags = sorted(glob.glob(os.path.join(root_directory,"**/*.bag"), recursive=True))

def imageData_from_csv(csv_file) :
    counter = 0

    idx = []
    t = []
    filenames = []

    if not os.path.exists(csv_file) and not os.path.isfile(csv_file) :
        # If we can't find the file first time around, 
        # try removing the _compressed from the filename
        csv_file = csv_file.replace('_compressedDepth','')
        csv_file = csv_file.replace('_compressed','')

    # Import the file if it exists
    if os.path.exists(csv_file) and os.path.isfile(csv_file) :
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)

            for row in reader:
                idx.append(counter)
                t.append(float(row[2]) + float(row[3])/1e9)
                filenames.append(row[5])
                counter += 1

    return idx, t, filenames

def get_closest_image(bagRoot,t_array,idx_array,filename_array,t_frame) :

    # Gets the image closest to the given time
    img = None

    if len(t_array) > 3 : 
        # idx_closest  = int(math.floor(np.interp(t_frame,t_array,idx_array)))
        idx_closest  = int((np.interp(t_frame,t_array,idx_array)))
        if idx_closest >= len(filename_array) :
            idx_closest = len(filename_array) - 1
        filename     = os.path.join(bagRoot,filename_array[idx_closest])  
        img          = cv2.imread(filename, -1)   # For 16-bit (might also work for 8-bit)
        # img_cam2          = cv2.imread(filename_cam2, cv2.IMREAD_COLOR) # for 8-bit 

    # If the image remains empty, fill with black
    if img is None :
        idx_closest = ''
        img = np.zeros((400,533,3), np.uint8)

    # Make sure img is 3-channel
    if len(img.shape) > 2 :
        if (img.shape[2] == 1) :
            img = cv2.merge([img,img,img])  

    return idx_closest, img

def uint16_2_uint8(img_dep) :

    # Converts 16-bit depth image to an 8-bit image

    if img_dep.dtype == 'uint8' :
        # Data already 8 bit
        return img_dep

    # Clip out obvious endpoints
    clipped_dep = img_dep[(10 < img_dep) & (img_dep < 65500)] 
    if len(clipped_dep) == 0 :
        # Image is likely empty, just return what we have
        return img_dep

    threshold_lo = np.percentile(clipped_dep,percentile_lo)  # 300
    threshold_hi = np.percentile(clipped_dep,percentile_hi)  # 5000
    img_dep[img_dep<threshold_lo] = threshold_lo
    img_dep[img_dep>threshold_hi] = threshold_hi
    cv2.normalize(img_dep, img_dep, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(img_dep, 8, img_dep)
    img_dep = np.uint8(img_dep)
    img_dep = cv2.applyColorMap(img_dep, cv2.COLORMAP_MAGMA)

    return img_dep

def mono_2_rgb(img) :
    # We probably should add a check in here to make
    # sure the image is actually still mono
    if len(img.shape) > 2 :
        if img.shape[2] == 3 :
            return img
    
    # Need to concatenate
    img = cv2.merge([img,img,img])

    return img

def add_black_border(image, target_width):
    height, width = image.shape[:2]
    border_width = target_width - width

    left_border = border_width // 2
    right_border = border_width - left_border

    padded_image = np.pad(image, [(0, 0), (left_border, right_border), (0, 0)], mode='constant')
    return padded_image

def vstack_images(img1, img2) :
    # Check images are the same size
    # We want to keep the height the same, so add width
    if img1.shape[1] > img2.shape[1] :
        img2 = add_black_border(img2, img1.shape[1])
    elif img1.shape[1] < img2.shape[1] :
        img1 = add_black_border(img1, img2.shape[1])
        
    # if len(img1) < 3 :
    #     img_seg1 = np.zeros(img_seg2.shape, np.uint8)
    # if len(img2) < 3 :
    #     img_seg2 = np.zeros(img_seg1.shape, np.uint8)
    imgOut = np.vstack([img1,img2])  # probably need to make it default to black image if missing
    
    return imgOut

def create_video(videoName,videoFrame_directory,framerate=30) :

    print("Generating .mp4")

    # Compile video frames into a .mp4 file
    output_path = os.path.split(videoFrame_directory)[0]
    output_name = os.path.join(output_path,videoName+".mp4")
    output_name_fast = os.path.join(output_path,videoName+"-fast.mp4")

    if os.path.exists(output_name) and os.path.exists(output_name_fast) :
        print(f"\t{output_name} already exists, skipping...")
        return

    cmd = "ffmpeg -framerate " + str(round(framerate)) + " -start_number 0 -i " \
        + os.path.join(videoFrame_directory,"%06d.jpg") + \
        " -vf \"pad=ceil(iw/2)*2:ceil(ih/2)*2,format=yuv420p\"  -vcodec libx265 -crf 30 -y " \
        + output_name
    os.system(cmd)

    # Create a sped up version of the video (easier for checking for stuff)
    cmd = "ffmpeg -i " + output_name + " -filter:v setpts=PTS/10 -y " + output_name_fast
    os.system(cmd)
 
def combine_videos(root_directory, output_file) :

    # Combines all videos found within a directory into a single file

    output_fullPath = os.path.join(root_directory,output_file+".mp4")

    # Find all .mp4 files
    mp4_files = sorted(glob.glob(os.path.join(root_directory,"**/*.mp4"), recursive=True))
    slow_videos = [entry for entry in mp4_files if '-fast' in entry]

    # output_directory = os.path.split(output_file)[0]
    videos_txt = os.path.join(root_directory,'videos_slow.txt')

    if mp4_files is None :
        print("No videos to combine, returning")
        return

    # Create a text file with the list of videos
    with open(videos_txt, 'w') as f:
        f.writelines([f"file {file}\n" for file in slow_videos])

    # Combine the videos
    cmd_video = "ffmpeg -f concat -safe 0 -i " + videos_txt + " -c copy -y " + output_fullPath
    os.system(cmd_video)

    # Remove the text file
    if os.path.exists(videos_txt):
        os.remove(videos_txt)

    return

def create_video_frames(bagfile) :

    print("Processing "+bagfile)
    
    # bagRoot = os.path.splitext(bagFull)[0]
    bagRoot = bagfile.split('/')[0:-1]
    bagRoot = '/' + os.path.join(*bagRoot)

    processedDir = os.path.join(bagRoot,'processed')

    ## Read csv files in by looping through array
    idx_array = np.empty(img_array.shape, dtype=object)
    t_array = np.empty(img_array.shape, dtype=object)
    files_array = np.empty(img_array.shape, dtype=object)

    for ii in range(img_array.shape[0]):
        for jj in range(img_array.shape[1]):
            idx_array[ii,jj], t_array[ii,jj], files_array[ii,jj] = imageData_from_csv(os.path.join(bagRoot,'csv',img_array[ii,jj]))

    # Check to make sure if we have timing data, if not, guess based on the highest number of frames
    img_ref = img_array_ref
    if len(t_array[img_ref]) == 0 :
        print("\tNo timing data, trying other elements")

        max_frames = 0

        for ii in range(img_array.shape[0]):
            for jj in range(img_array.shape[1]):
                if len(t_array[ii,jj]) > max_frames :
                    max_frames = len(t_array[ii,jj])
                    img_ref = (ii,jj)
        if max_frames > 10 :
            print(f"\t\tNow using {img_ref} for timing data ({max_frames} frames)")
        else :
            print("Not enough data, skipping this video")
            return 0

    # Calculate framerate
    frame_rate = math.ceil(len(t_array[img_ref])/(t_array[img_ref][-1] - t_array[img_ref][0]))

    # Skip if the timing frame data doesn't exist
    if len(idx_array[img_ref]) < 5 :
        print("\tMissing reference camera information, skipping...")
        return None

    # Create output folder only if we haven't processed these files yet
    # matches the number of messages in the bag file
    if (os.path.exists(processedDir)) :
        n_images_expected = len(idx_array[img_ref])
        n_images_actual = len([file for file in os.listdir(processedDir) if os.path.isfile(os.path.join(processedDir, file))])
        if (n_images_expected == n_images_actual) :
            print("\tVideo frames already created, skipping...")
            return frame_rate
        if (n_images_expected != n_images_actual) :
            print("\tVideo frame count mismatch - re-extracting...")
            print(f"\t\tGot {n_images_actual}, expected {n_images_expected}")

    # Delete existing data and re-create
    if os.path.exists(processedDir) :
        shutil.rmtree(processedDir)
    os.makedirs(processedDir)

    # Loop through all the frames
    counter = 0
    subcounter = 0
    for t in t_array[img_ref] :

        if (0) :
            if (subcounter % 10) :
                # Skip all but the 10th image
                subcounter += 1
                continue
            else :
                # This is the 10th image, process it
                subcounter += 1
                pass

        # Work out which (and open) files we're going to display
        frame_idx_array = np.empty(img_array.shape, dtype=object)
        frame_img_array = np.empty(img_array.shape, dtype=object)
        imgOut = None

        for jj in range(img_array.shape[1]):     # columns
            
            imgOut_row = None
            
            for ii in range(img_array.shape[0]): # rows

                # Import the images
                frame_idx_array[ii,jj], frame_img_array[ii,jj] = get_closest_image(bagRoot,t_array[ii,jj],idx_array[ii,jj],files_array[ii,jj],t) 

                # Process any non-rbg8 images into something useful
                frame_img_array[ii,jj] = uint16_2_uint8(frame_img_array[ii,jj])
                frame_img_array[ii,jj] = mono_2_rgb(frame_img_array[ii,jj])

                # Rotate image if required
                if payload_inverted :
                    frame_img_array[ii,jj] = cv2.rotate(frame_img_array[ii,jj], cv2.ROTATE_180)


                # Debug looking at the image
                # cv2.imshow('test',frame_img_array[ii,jj])
                # cv2.waitKey(0)

                # Make all images the same height (and add label)
                height = 400
                color = (255,255,255)
                fontScale = 0.5
                fontThickness = 1 

                width = round(frame_img_array[ii,jj].shape[1]/frame_img_array[ii,jj].shape[0]*height) # Scale width to the given height
                dim = (width, height)
                frame_img_array[ii,jj] = cv2.resize(frame_img_array[ii,jj],dim)  

                cv2.putText(frame_img_array[ii,jj],str(frame_idx_array[ii,jj]), \
                    (10,height-10), cv2.FONT_HERSHEY_SIMPLEX, fontScale, color, fontThickness)

                # Stack each image in the column together
                if imgOut_row is None:
                    imgOut_row = frame_img_array[ii,jj]
                else :
                    imgOut_row = np.vstack([imgOut_row,frame_img_array[ii,jj]])

            # Horizontally stack each column of images together
            if imgOut is None:
                imgOut = imgOut_row
            else:
                imgOut = np.hstack([imgOut,imgOut_row])

        # Save the image
        cv2.putText(imgOut,bagRoot.split('/')[-1], \
            (10,15), cv2.FONT_HERSHEY_SIMPLEX, fontScale, color, fontThickness)

        imgName = ('%06d' % counter) + '.jpg'
        filename_output = os.path.join(processedDir,imgName)
        cv2.imwrite(filename_output,imgOut, [int(cv2.IMWRITE_JPEG_QUALITY), 70]) 

        # Debug image view
        # cv2.imshow('test',imgOut)
        # cv2.waitKey(0)

        # Update the counter
        counter += 1
        if (counter % 100 == 0) :
            t_offset = float(t)-float(t_array[img_ref][0])
            print("\x1b[1K\r\t(" + ('%5d' % counter) + "/"+str(len(t_array[img_ref]))+") t: "+('%5.1f' % t_offset)+" ",end='')

    # Frames created for bagfile
    return frame_rate


print("=================================")
print(" Generating Videos for Bag Files")
print('   '+root_directory)
print("=================================\n")
print("Found " + str(len(bags)) + " bags")

# Exit if no bags exist
if len(bags) == 0 :
    exit(0)

# Print bag names
for bagName in bags:
    print("\tFound "+bagName)

# Process bags
for bagFullPath in bags :

    # Split up names, etc.
    bagDir =  bagFullPath.split('/')[0:-1]
    bagRoot = '/' + os.path.join(*bagDir)
    bagName = bagDir[-1]
    processedDir = os.path.join(bagRoot,'processed')

    # Create video
    frame_rate = create_video_frames(bagFullPath)
    if frame_rate is not None :
        create_video(os.path.join(bagRoot,bagName),processedDir,framerate=frame_rate)

# Combine videos
combine_videos(root_directory,'combined')