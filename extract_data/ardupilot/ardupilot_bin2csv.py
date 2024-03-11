from pymavlink import DFReader
import os
import glob
import datetime

# Import Folder
root_directory = '/data'

def bin2csv(log_filename):

    # Import Log
    print(f"Processing {log_filename}")
    if log_filename.endswith('.log'):
        log = DFReader.DFReader_text(log_filename)
    else:
        log = DFReader.DFReader_binary(log_filename)

    # File was opened, create directory for saving data
    output_path = os.path.join(os.path.splitext(log_filename)[0])
    if not os.path.exists(os.path.join(output_path,'csv')):
        os.makedirs(os.path.join(output_path,'csv'))

    # Save parameter files
    print(f"\tSaving parameter file")
    fid = open(os.path.join(output_path,'params.txt'), 'w')
    timestamp = datetime.datetime.fromtimestamp(log.clock.timebase).strftime("%Y-%m-%d-%H-%M-%S")
    print(f"# Parameters exported from {log_filename}\n# {timestamp}\n#",file=fid)
    for param, value in sorted(log.params.items()) :
        print(f"{param}={value}",file=fid)
    fid.close()
    print(f"\t\t{len(log.params)} parameters written")

    # Save each data stream
    print('\tImporting data streams')
    skip_fmt_name = ['FMT','PARM','UNIT','MULT','FMTU']
    fid = {}
    line = []

    while line is not None :

        # Read the line
        line = log._parse_next()

        # Check for empty lines (assume end of file)
        if line is None :
            continue

        # Check for non-data lines
        if line.fmt.name in skip_fmt_name :
            continue

        # Handle multiple instances of sensors
        if line.fmt.instance_field is None :
            channel_name = line.fmt.name
        else :
            channel_name = line.fmt.name + '_' + str(line._elements[line.fmt.colhash[line.fmt.instance_field]])

        # Handle multipliers
        if line._apply_multiplier :
            for idx, multi in enumerate(line.fmt.msg_mults):
                if multi is not None :
                    line._elements[idx] = line._elements[idx]*multi

        # Open a text file if not already open
        if channel_name not in fid :

            # Open the file
            fid[channel_name] = open(os.path.join(output_path,'csv',channel_name+'.csv'), 'w')

            # Write the header
            print(*line._fieldnames, sep=', ',file=fid[channel_name])

        # Write the data
        print(*line._elements, sep=', ',file=fid[channel_name])

        # Update the user
        if log.remaining % 10000 == 0 :
            print(f"\033[K\t\t{log.remaining} lines remaining",end='\r')

    # Close open files
    for files in fid :
        fid[files].close

    # All done
    print(f"\033[K\t\tDone")
    return

if __name__ == "__main__":

    # Find all *.bin files
    log_files = sorted(glob.glob(os.path.join(root_directory,"**/*.bin*"), recursive=True))

    # Import the file
    for ii in range(len(log_files)):
        print(f'{ii+1:2d}/{len(log_files):2d} | ', end='')
        bin2csv(log_files[ii])

    # All done
    print("All log files imported!")
    exit (0)