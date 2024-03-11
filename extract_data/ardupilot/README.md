# ArduPilot bin2csv Converter
A python script for directly exporting ArduPilot bin logs to a set of csv files for each data group.
The script searches recursively for all *.bin files in a directory, making export of both individual and large numbers of logs simple. 

## Dependencies
The main log import function are provided by pymavlink.
Dependencies are stored in the `requirements.txt` file which can be installed using
```
pip install -r requirements.txt
```

Tested on Ubuntu 20.04 but should be cross-platform.

## Running the Code
### Stand-alone Python Script
To run the script from stand-alone python
- Edit the line `root_directory = '/data'` in `ardupilot_bin2csv.py` to match your data directory
- Run the extraction script `python3 ardupilot_bin2csv.py`

### Docker Container
To run the extraction process via a docker container
- Modify `run_docker.sh` to point towards the root directory containing the log files
- Run the script `./run_docker.sh` to build and run the script
