#!/bin/bash

# exit when any command fails
set -e

# Delete all images on system
# docker system prune -a
# Clean out in-between builds
# docker system prune -f

echo "Building and starting bag processing docker image"

docker build -t bag_processing -f Dockerfile .

FOLDER_TO_EXPORT=/home/user/bags/

# Run all the scripts
docker run -it --net=host --user $(id -u):$(id -g) --mount type=bind,source=$FOLDER_TO_EXPORT,target=/data bag_processing

# Debugging
# docker run -it --net=host --user $(id -u):$(id -g) --mount type=bind,source=$FOLDER_TO_EXPORT,target=/data bag_processing sh -c /app/reindexBags.py
# docker run -it --net=host --user $(id -u):$(id -g) --mount type=bind,source=$FOLDER_TO_EXPORT,target=/data bag_processing sh -c /app/rosbagExtract.py
# docker run -it --net=host --user $(id -u):$(id -g) --mount type=bind,source=$FOLDER_TO_EXPORT,target=/data bag_processing sh -c /app/createVideo.py
# docker run -it --net=host --user $(id -u):$(id -g) --mount type=bind,source=$FOLDER_TO_EXPORT,target=/data bag_processing sh -c /app/compressExtractionOutputs.py
# docker run -it --net=host --user $(id -u):$(id -g) --mount type=bind,source=$FOLDER_TO_EXPORT,target=/data bag_processing bash 
