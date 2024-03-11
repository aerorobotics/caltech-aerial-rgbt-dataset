#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   rosbagExtract.py
#
#   This library provides ROS bag extraction of:
#   - topic messages into CSVs
#   - image messages into jpg (8-bit) or tiff (16-bit)
#
#   To Use:
#     Change the 'root_directory' variable to point to the folder with
#     your bag files and then run this script.  The script will recursively
#     search for bagfiles and extract the desired topics
#   
#   Selecting Extract Topics:
#     Modify the IMAGE_BAG_TOPICS and CSV_BAG_TOPICS variables, using regex
#     to specify the bags
#        All topics containing the string -> r'/imu/imu*'
#        Exact match to the string -> r'^/imu/imu/$'
#
#   To Add to Your Own Code:
#     from rosbagExtract import extractFromBags
#        - or -
#     from rosbagExtract import csvExtract, imageExtract, extractFromBags
#     extractFromBags([(csvExtract, 'csv'), (imageExtract, 'eo')])
#
#   Written by the Aerospace Robotics and Controls Group - Caltech
#

# General imports
import os
import re
import shutil
import csv
import glob
import subprocess
import argparse
import multiprocessing
import pdb

# ROS and image related imports
import rosbag
import bagpy
import cv2
import numpy as np  # Might be able to remove this once done
from sensor_msgs.msg import Image
from grid_map_msgs.msg import GridMap
from cv_bridge import CvBridge

print("All packages imported!\n")

# Directory to search
# root_directory = os.path.join(os.getcwd(),'data') 
root_directory = '/data'

# Topics we want to extract
IMAGE_BAG_TOPICS = [
    re.compile(r'/*'),        # Extract all topics
    re.compile(r'/eo/*'),     # Extract specific topics
    re.compile(r'/boson/*'),
]

GRIDMAP_BAG_TOPICS = [
    re.compile(r'/*'),
]

CSV_BAG_TOPICS = [
    re.compile(r'/*'),
    re.compile(r'/imu/imu*'),
    re.compile(r'/uav1/mavros/imu/data*'),
    re.compile(r'/uav1/mavros/local_position/*'),
    re.compile(r'/uav1/mavros/distance_sensor/lidar*'),
    re.compile(r'/uav1/mavros/global_position/global'),
    re.compile(r'/sync/rate*'),
    re.compile(r'/gps*'),
]

# regex for bags
BAGFILE_FORMAT = "**/*.bag*"

# index formats
COUNT = '({}/{}) - {}'

# Searching for bag messages
NO_BAG_MSG = 'NO EXTRACTION PROCESS\n\nNo bag files found with format: ' + BAGFILE_FORMAT
FOUND_BAG_MSG = 'STARTING EXTRACTION PROCESS\n\nBags found:'

# checking acceptable file extraction methods
CSV_EXTRACT_NAME = 'csv'
IMG_EXTRACT_NAMES = ['image']
NOT_EXTRACT_MSG = 'Ignoring {} as not recognized file extraction method\n'

# Creating bag directory messages
DIR_NEW_MSG = 'Created {} folder: {}'
DIR_FOUND_MSG = 'Using already created {} folder: {}'

# header file extraction messages
EXTRACT_NAMES_MSG = 'Will extract:'
START_PROCESS_BAG_MSG = '{:3d}/{:3d} | START PROCESSING OF {}'
END_PROCESS_BAG_MSG = 'ENDING PROCESSING OF {}\n\n'

EXTRACT_START_MSG = '{} EXTRACT START'
EXTRACT_END_MSG = '{} EXTRACT DONE\n\n'

# when searching for topics
NO_TOPICS_MSG = '\t\tNo desired topics found in {}\n'

# Indent format left and right for helper function
INDENT_FORMAT_LEFT = '{:<'
INDENT_FORMAT_RIGHT = '}'

# standard unit of indent (number of spaces)
INDENT_CONST = 3

# input into format when indenting.
EMPTY = ''

# count index formats
COUNT = '{:3d}/{:3d} | {}'

# Run in parallel?
RUN_IN_PARALLEL = False

# If we have an arg, override the root_directory variable
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', type=str, default=root_directory, help='Path to rosbag files')
args = parser.parse_args()
root_directory = args.path

# -------------------- Message functions --------------------

def getWantedTopics(topics,filter) :
    wantedTopics = [element for element in topics if any(pattern.match(element) for pattern in filter)]
    return wantedTopics

def indent_msg(msg, amt = 1):
    """
    Helper method for indenting messages

    :param msg: message to indent
    :param amt: amount of desired indentation
    :return: message which will be indented when <msg>.format() is used
    """
    return INDENT_FORMAT_LEFT + str(amt * INDENT_CONST) + INDENT_FORMAT_RIGHT + msg

# ---------------------- Bag functions ----------------------

def findBags(dir):
    """
    Find all bag files in current directory with BAGFILE_FORMAT

    :return: list of all bag files in current directory
    """

    # Find all the bag files in the directory
    #bags = [fn for fn in os.listdir(root_directory) if re.search(BAGFILE_FORMAT, fn)]
    
    bags = sorted(glob.glob(os.path.join(dir,BAGFILE_FORMAT), recursive=True))

    # Return the list
    return bags

def extractBagDirectory(root_directory) :
    """
    Apply an extractor functions to all bag files in current directory
    and save the output in a folder named after the file types
    extracted inside each bags general folder.

    :param extractMethods: List of tuples of extraction functions and
                           corresponding name of files to be extracted
    """
    bagNames = findBags(root_directory)

    # print bag filenames
    bagTotal = len(bagNames)
    if not bagNames:
        print(NO_BAG_MSG)
        return
    else:
        print(FOUND_BAG_MSG.format(bagTotal))
        for i in range(bagTotal):
            bagName = bagNames[i]
            print(COUNT.format(i+1, bagTotal, bagName))
        print()

    if (RUN_IN_PARALLEL) :

        print("Running job in parallel")
        print("This could get messy...")

        # Create a pool of worker processes
        pool = multiprocessing.Pool()

        # Map the process_bag function to each bag name in parallel
        pool.map(process_bag, bagNames)

        # Close the pool of worker processes
        pool.close()
        pool.join()

    else :

        # Process in series.  Easier to debug issues
        counter = 1
        for bagName in bagNames :
            print(
                "=============== Bag ", 
                counter,
                " of ",
                bagTotal,
                " ===============\n" )
            print(f"\n{bagName}\n")
            process_bag(bagName)
            counter = counter + 1

    return

def process_bag(bagName) :
        # Add the root_directory onto the bag name
        bagName = os.path.join(root_directory,bagName)

        # Check the bag
        # bagName = checkBag(bagName)  # Slow and I don't think we need it.  We can reindex the bags elsewhere

        # start extraction for bag
        with rosbag.Bag(bagName,'r') as bagFile :
            # Get a list of topics
            topics = bagFile.get_type_and_topic_info()

            # Extract topics
            imageExtract(bagFile, getWantedTopics(topics.topics,IMAGE_BAG_TOPICS))
            gridmapExtract(bagFile, getWantedTopics(topics.topics,GRIDMAP_BAG_TOPICS))
            csvExtract(bagFile, getWantedTopics(topics.topics,CSV_BAG_TOPICS))

# ---------------------- rosbag check ----------------------
# Fixes any bags that haven't closed properly

def checkBag(bagName) :

    print("\tChecking rosbag")

    output = subprocess.run(["rosbag", "check", bagName], 
                                text=True,
                                capture_output=True)

    if "ERROR bag unindexed" in output.stderr :
        print(f"    Reindexing {os.path.basename(bagName)}...",end='')

        # Re-index the file
        output_dir = os.path.join(os.path.dirname(bagName),"reindexed")
        os.makedirs(output_dir)
        output = subprocess.run(['rosbag','reindex','--output-dir='+output_dir,bagName],
                                    text=True,
                                    capture_output=True)

        # Move and replace the un-indexed file, removing the .active part
        bagFrom = os.path.join(output_dir,os.path.basename(bagName))
        bagTo = bagName.rstrip('.active')
        shutil.move(bagFrom, bagName)
        shutil.move(bagName, bagTo)
        shutil.rmtree(output_dir)
        print("Done!")

        # Return the new bag name
        return (bagTo)

    # The bag was fine, straight return the old name
    return (bagName)

# ---------------------- csv extract function ----------------------

CSV_EXT = '.csv'

# for timestamp csv
IMG_CSV_HEADERS = ['Time', \
                   'header.seq', 'header.stamp.secs', 'header.stamp.nsecs', 'header.frame_id', \
                   'filename']

FAILED_CSV_MSG = 'FAILED EXTRACTION of {}:'
BAGPY_LOG_MSG = 'BAGPY READER LOG:'
TOPIC_FOLDER_MSG = '{:<30} -> {}'


def csvExtract(bagFile,topic_list):
    """
    Convert messages of desired topics in a bag to a CSV

    :param bagName: filename of bag from which we want
                    to extract topic messages
    """

    print("\tExtracting csv files")

    # Create a folder for the data
    extractFolder = os.path.join(os.path.dirname(bagFile.filename),'csv')

    if (not os.path.exists(extractFolder)) :
        os.makedirs(extractFolder)
        print("\t\tCreated "+extractFolder)

    print()
    counter = 0

    try:

        # Return if not topics to extract
        if topic_list is None :
            return
        
        topicTotal = len(topic_list)
        
        # Use bagpy to handle the CSV extraction
        bagReader = bagpy.bagreader(bagFile.filename)

        for topic in topic_list :

            counter = counter+1
            
            # Check to make sure that we are extracting a csv-ish topic type
            info = bagFile.get_type_and_topic_info(topic_filters=topic)
            msg_type = info.topics[topic][0]
            if (msg_type == 'sensor_msgs/CompressedImage') \
                or (msg_type == 'sensor_msgs/Image') \
                or (msg_type == 'sensor_msgs/PointCloud2') \
                or (msg_type == 'grid_map_msgs/GridMap') \
                or (msg_type == 'tf2_msgs/TFMessage') :
                print(f"\tNot extracting {topic}, type {msg_type} as csv")
                continue

            # Generate all the names
            csvName = topic.replace('/', '_') + CSV_EXT
            csvNewPath = os.path.join(os.getcwd(), extractFolder, csvName)
            
            if (os.path.isfile(csvNewPath)) :
                # No need to re-extract something that exists
                print(COUNT.format(counter, topicTotal, topic + " > Already exists, skipping..."))
                continue

            # Extract the topic as csv
            print( COUNT.format(counter, topicTotal, TOPIC_FOLDER_MSG.format(topic, csvNewPath)))
            csvCurPath = bagReader.message_by_topic(topic)
            shutil.move(csvCurPath, csvNewPath)

    except Exception as e:
        print(FAILED_CSV_MSG.format(topic))
        print(e)
    finally:
        # Delete the temporary folder
        if (os.path.isdir(os.path.splitext(bagFile.filename)[0])) :
            shutil.rmtree(os.path.splitext(bagFile.filename)[0])

        # just in case (reader has no close method)
        if 'bagReader' in locals():
            del bagReader

    print() # newline for ending
    return

# ---------------------- image extract function ----------------------

# Info messages for image extraction processes
IMG_COUNT = 'Frame '
FAILED_IMG_MSG = 'STOPPING: failed extraction of frame {}'
EXTRACT_FOLDER_MSG = '{:<10}: '

def imageExtract(bagFile,topic_list):
    """
    Extract image image data from desired topics in a bag and create a CSV
    documenting the timestamp for each image.

    :param bagName: filename of bag from which we want
                    to extract EO data
    """

    print("\tExtracting image data")

    # Return if no topics to extract
    if topic_list is None :
        return
        
    topicTotal = len(topic_list)

    # extract images using cv bridge
    cvBridge = CvBridge()
    try:
        for i in range(topicTotal):

            topic = topic_list[i]
            count = 0

            # Work out file paths/names
            camera_name = ''
            csvName   = topic.replace('/', '_') + CSV_EXT
            csvFolder = os.path.join(os.path.dirname(bagFile.filename),'csv')
            topicNameSplit = topic.split('/')

            # Work out folder names
            imgFolder = os.path.join(os.path.dirname(bagFile.filename),'images')
            for topic_part in topicNameSplit :
                imgFolder = os.path.join(imgFolder,topic_part)

            csvPath   = os.path.join(csvFolder, csvName)

            # Check to make sure that we are an ok topic type
            info = bagFile.get_type_and_topic_info(topic_filters=topic)
            msg_type = info.topics[topic][0]

            if (msg_type == 'sensor_msgs/CompressedImage') \
                or (msg_type == 'sensor_msgs/Image') :

                # These are known good message type, allow them
                print("\t\tProcessing " + topic)
                
            elif (msg_type == 'dynamic_reconfigure/ConfigDescription') \
                or (msg_type == 'dynamic_reconfigure/Config') \
                or (msg_type == 'sensor_msgs/CameraInfo') \
                or (msg_type == 'bond/Status') :

                # Known unsupported type, skip
                # print("\t\t\tSkipping known non-image type message "+msg_type)
                continue

            else :
                
                # Known unsupported type, simply pass (good for debugging)
                # print("\t\tTopic "+ topic +" of type "+msg_type+" is currently unsupported for image extract, skipping...")
                continue

            # Check to see if we've already extract images for this file.
            # Check the csv exists, then that the number of images extracted
            # matches the number of messages in the bag file
            if (os.path.exists(csvPath)) :
                n_images_expected = bagFile.get_message_count(topic_filters=topic)
                n_images_actual = len([file for file in os.listdir(imgFolder) if os.path.isfile(os.path.join(imgFolder, file))])
                if (n_images_expected == n_images_actual) :
                    print("\t\t\tAlready extracted, skipping...")
                    continue
                if (n_images_expected != n_images_actual) :
                    print("\t\t\tImage count mismatch - re-extracting...")

            # Create the output folders if they don't exist
            if (not os.path.exists(csvFolder)) :
                os.makedirs(csvFolder)
                print("\t\tCreated " + csvFolder)
            
            if (not os.path.exists(imgFolder)) :
                os.makedirs(imgFolder)
                print("\t\tCreated " + imgFolder)

            # Start the csv file
            csvFile = open(csvPath, 'w', newline='')
            csvWriter = csv.writer(csvFile, delimiter=',')
            csvWriter.writerow(IMG_CSV_HEADERS)

            # Loop through and extract data
            for topic, msg, t in bagFile.read_messages(topic):
                if (msg._type == 'sensor_msgs/CompressedImage') :
                    cvImg = cvBridge.compressed_imgmsg_to_cv2(msg, desired_encoding="passthrough")

                    # Fix image encoding
                    if 'bayer_rggb8' in msg.format :
                        cvImg = cv2.cvtColor(cvImg,cv2.COLOR_BayerBG2BGR )
                
                elif (msg._type == 'sensor_msgs/Image') :
                    cvImg = cvBridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")

                    # Fix image encoding
                    if 'rgb8' in msg.encoding :
                        cvImg = cv2.cvtColor(cvImg,cv2.COLOR_RGB2BGR )

                else :
                    # Unknown not image type
                    print("Message type " + msg._type + " not supported!")
                    print("\tSkipping " + topic)
                    continue
                
                # Skip this round if no image imported
                if cvImg is None :
                    continue

                # Extension type depends on data type for cvImg
                if (cvImg.dtype == '<u2') :
                    # Thermal image
                    imgExt = '.tiff'
                else :
                    # Other images
                    imgExt = '.jpg'

                imgName = 'image' + '-' + ('%05d' % count) + imgExt
                imgFullName = os.path.join(imgFolder, imgName) 
                cv2.imwrite(imgFullName, cvImg)

                bagFolder = os.path.split(bagFile.filename)[0]
                imgRelativeName = imgFullName.replace(bagFolder,'')[1:]

                # Write to CSV file
                csvWriter.writerow( [
                    "{:.7f}".format(t.to_sec()), \
                    msg.header.seq, \
                    msg.header.stamp.secs, \
                    msg.header.stamp.nsecs, \
                    msg.header.frame_id, \
                    imgRelativeName])

                # Print something so we know the process is happening
                if (count % 100 == 0) :
                    print('\x1b[1K\r\t\t\tFrame: '+str(count)+'/'+str(bagFile.get_message_count(topic))+' ',end='')

                # Update the counter
                count += 1

            csvFile.close()

            print('\x1b[1K\r\t\t\tFrame: '+str(count)+'/'+str(bagFile.get_message_count(topic))+' ')

    except Exception as e:
        print(FAILED_IMG_MSG.format(count))
        print(e)

    # All done :)
    print()
    return

# ---------------------- gridMap extract function ----------------------
def gridmapExtract(bagFile,topic_list):
    """
    Extracts gridMap data from Image toics
    from ROS bag files.

    :param bagName: 
        -bag file name
    """   

    print("\tExtracting gridMap data")

    # If no topics, return functions
    if topic_list is None :
        return

    # Extract gridmap using cv bridge
    cvBridge = CvBridge()

    imgFolder = os.path.join(os.path.dirname(bagFile.filename),'images')
    csvFolder = os.path.join(os.path.dirname(bagFile.filename),'csv')

    try:
        for topic in topic_list:
            
            # Check to make sure that we are an ok topic type
            info = bagFile.get_type_and_topic_info(topic_filters=topic)
            msg_type = info.topics[topic][0]

            if (msg_type == 'grid_map_msgs/GridMap') :
                # These are known good message type, allow them
                print("\t\tProcessing " + topic)
            else :
                # Known unsupported type, simply pass (good for debugging)
                # print("\t\tTopic "+ topic +" of type "+msg_type+" is currently unsupported for gridmap message extract, skipping...")
                continue
            
            # Total frame counter    
            frame_count = 0

            # image index counter
            imgName_index = 0

            # Loop through topic msgs and extract gridMap data
            for _, msg, t in bagFile.read_messages(topic):

                # Loop through msg layers and extract layer data
                for layer_count, layer in enumerate(msg.layers):
                    
                    # Make sure layer is an alphabetic and not numeric layer 
                    # For example ['elevation'] is ok, but ['-1.570796'] is not.
                    # matt: seems to work fine allowing numeric names here, so let's let it
                    #       try and see what break (if it does in the future)
                    if layer.replace('_', '').isalpha() or 1:

                        # Work out the files and directory names/paths for images and csv files
                        topic_msg_layer = os.path.join(topic[1:], layer)
                        img_folder = os.path.join(imgFolder, topic_msg_layer)
                        csvName = topic.replace('/', '_')+'_' + layer + CSV_EXT

                        csvPath = os.path.join(csvFolder, csvName)
                        
                        # Check to see if we've already extract images for this file.
                        # Check the csv exists, then that the number of images extracted
                        # matches the number of messages in the bag file
                        if (os.path.exists(csvPath)) :
                            n_images_expected = bagFile.get_message_count(topic_filters=topic)
                            n_images_actual = sum(1 for _, _, files in os.walk(img_folder) for f in files)
                            if (n_images_expected == n_images_actual) :
                                print("\t\tAlready extracted, skipping...")
                                break
                            if (n_images_expected != n_images_actual) :
                                pass
                                # print("\t\tImage count mismatch - re-extracting...")

                        # Create the image subdirectories per layer
                        if not os.path.exists(img_folder):
                            os.makedirs(img_folder)
                            print("\n\t\tCreated " + img_folder, end='')

                        # Create csv directory
                        if not os.path.exists(csvFolder):
                            os.makedirs(csvFolder)
                            print("\n\t\tCreated " + csvFolder, end='')

                        # Add headers to csv file
                        if not os.path.exists(csvPath):
                            # Add top row with headers if CSV file doesn't exist
                            with open(csvPath, 'w', newline='') as csv_file:
                                csv_writer = csv.writer(csv_file)
                                csv_writer.writerow(IMG_CSV_HEADERS)

                        # convert grid map to cv image
                        axis_length = int(np.sqrt(len(msg.data[layer_count].data)))
                        image_np = np.reshape(msg.data[layer_count].data, (axis_length, axis_length))
                        threshold_lo = np.percentile(image_np, 5)
                        threshold_hi = np.percentile(image_np, 95)
                        image_np[image_np < threshold_lo] = threshold_lo
                        image_np[image_np > threshold_hi] = threshold_hi
                        cv2.normalize(image_np, image_np, 0.0, 255.0, cv2.NORM_MINMAX)
                        image_np = np.uint8(image_np)
                        cvImg = cv2.applyColorMap(image_np, cv2.COLORMAP_MAGMA)

                        if cvImg.dtype == '<u2':
                            # Thermal image
                            imgExt = '.tiff'
                        else:
                            # Other images
                            imgExt = '.png'

                        # Work out the image name
                        imgName = 'image_' + str(imgName_index) + '_' + layer + imgExt
                        imgPath = os.path.join(img_folder, imgName)
                        cv2.imwrite(imgPath, cvImg)

                        # Write to CSV file
                        with open(csvPath, 'a', newline='') as csv_file:
                            csv_writer = csv.writer(csv_file, delimiter=',')
                            csv_writer.writerow([
                                "{:.7f}".format(t.to_sec()), \
                                msg.info.header.seq, \
                                msg.info.header.stamp.secs, \
                                msg.info.header.stamp.nsecs, \
                                msg.info.header.frame_id, \
                                imgPath])
                    
                    frame_count += 1

                else:
                    # This will execute if the inner loop completes normally (without breaking)
                    imgName_index += 1
                    # progress bar in form of frame counter
                    if (frame_count % 100 == 0 and frame_count > 0) :
                        print('\x1b[1K\r\t\t\tFrame: '+str(frame_count)+'/'+str(bagFile.get_message_count(topic)*len(msg.layers))+' ',end='')

                    continue
                break  

            print('\x1b[1K\r\t\t\tFrame: '+str(frame_count)+'/'+str(bagFile.get_message_count(topic)*len(msg.layers))+' ')

    except Exception as e:
        print(FAILED_IMG_MSG.format(frame_count))
        print(e)

    # newline for ending
    print()
    return

# ----------------------  EXTRACTION  ----------------------

def main():
    """Extract CSVs and images from ROS bags in provided directory"""
    str = "Extracting files from "+root_directory
    print("\n\n")
    print('=' * len(str))
    print(str)
    print('=' * len(str))
    print("\n\n")

    extractBagDirectory(root_directory)

if __name__ == '__main__':
    main()
