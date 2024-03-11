#!/bin/bash

# exit when any command fails
set -e

# Delete all images on system
# docker system prune -a
# Clean out in-between builds
# docker system prune -f

echo "Building and starting ardupilot csv export script"

docker build \
    --build-arg USER_UID=$(id -u) --build-arg USER_GID=$(id -g) \
    -t ardupilot_bin2csv -f Dockerfile .

FOLDER_TO_EXPORT=/home/user/data/

# Run all the scripts
docker run -it --net=host --user $(id -u):$(id -g) --mount type=bind,source=$FOLDER_TO_EXPORT,target=/data ardupilot_bin2csv

# Debugging
# docker run -it --net=host --user $(id -u):$(id -g) --mount type=bind,source=$FOLDER_TO_EXPORT,target=/data ardupilot_bin2csv bash 
