#!/bin/bash

# Entrypoint script for running the docker
#   If runnnig as an entrypoint, can extract multiple
#   folders at once from docker (no bash file changes while running)

# exit when any command fails
set -e

# Run all the scripts
# /app/reindexBags.py
# /app/decompressBags.py
# /app/compressBags.py
/app/rosbagExtract.py
# /app/createVideo.py
# /app/compressExtractionOutputs.py
# /app/extractExtractionOutputs.py
