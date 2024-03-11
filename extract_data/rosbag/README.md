
# Bag Processing

Scripts to extract rosbags out to human-readable formats.
The code will recursively extract all rosbags so you may extract as few or as many bags as required.

## Running the Extraction
The easiest way is via docker.  
- Install docker on your computer
  - Follow the installation instructions at https://docs.docker.com/engine/install/
- Edit the file `run_docker.sh` to set the folder to search through.
  - These files are mounted as volumes in the docker
- Edit the file `entrypoint.sh` to set what scripts to run
  - The setup is defaulted to simply extract the bagfiles only
- Run the dockerfile via `./run_docker.sh`

Alternately, as the scripts are written in python3, you should be able to manually install the requirements and run directly from your computer.

## Included Scripts

### /scripts/reindexBags.py
This script reindexes bags to fix any `.active` bags automatically.

### /scripts/decompressBags.py
Decompresses bags back to uncompressed.  This is useful if you wish to change the compression scheme of the bags (in combination with compressBags).

### /scripts/compressBags.py
Recursively compresses any bags which are not already compressed. This helps save space on your computer.

### /app/rosbagExtract.py
Extracts bags out to human-readable formats (csv, jpg).

### /scripts/createVideo.py
Automatically creates videos using the extracted data from `rosbagExtract.py`.  Set the topics near the top, then the script compiles the frames then creates the video using `ffmpeg`.

### /scripts/compressExtractionOutputs.py
Automatically compress the `csv`, `images`, and `processed` folders to make moving files around easier (and to save space).

### /scripts/extractExtractionOutputs.py
Extract any zip files recursivey.

