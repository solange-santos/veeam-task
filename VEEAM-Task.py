# For synchronization of two folders
import os
import shutil

# For log file creation/copying/removal operations
import logging

# For periodical synchronization
import sched
import time

# For command line arguments
import argparse


###########################################################################################
#                                                                                         #
# def setup_logging(log_file)                                                             #
#                                                                                         #
# Function to create a log file, if such file doesn't exist already, and to configurate   #
# such logging (which should be performed not only to a file, but also to the console     #
# output)                                                                                 #
# Inputs: log_file (path to log file)                                                     #
#                                                                                         #
# Author: Solange Santos                                                                  #
# Date: 14/04/2024                                                                        #
#                                                                                         #
###########################################################################################
def setup_logging(log_file):
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create log file if it doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, 'w'):
            pass

    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


###########################################################################################
#                                                                                         #
# def sync_folders(source_folder, replica_folder, log_file)                               #
#                                                                                         #
# Function to synchronize two folders (source and replica). The synchronization is done   #
# in one-way: after the synchronization, content of the replica folder should be modified #
# to exactly match content of the source folder. File creation/copying/removal operations #
# are logged to a file and to the console output                                          #
# Inputs: source_folder (path to source folder)                                           #
#         replica_folder (path to replica folder)                                         #
#         log_file (path to log file)                                                     #
#                                                                                         #
# Author: Solange Santos                                                                  #
# Date: 14/04/2024                                                                        #
#                                                                                         #
###########################################################################################
def sync_folders(source_folder, replica_folder, log_file):
    # Ensure source folder exists
    if not os.path.exists(source_folder):
        logging.error(f"Source folder '{source_folder}' does not exist.")
        return

    # Ensure replica folder exists, create if not
    if not os.path.exists(replica_folder):
        logging.info(f"Created directory: {replica_folder}")
        os.makedirs(replica_folder)

    # Get list of files in source folder
    source_files = os.listdir(source_folder)

    # Copy files from source folder to replica folder
    for file_name in source_files:
        source_path = os.path.join(source_folder, file_name)
        replica_path = os.path.join(replica_folder, file_name)
        if os.path.isdir(source_path):
            sync_folders(source_path, replica_path, log_file)
            # Doesn't need a log here because it will be performed in condition "if not os.path.exists(replica_folder)"
            # when calling the function again
            # logging.info(f"Created directory: {replica_path}")
        else:
            shutil.copy2(source_path, replica_path)
            logging.info(f"Copied file: {source_path} to {replica_path}")

    # Remove any files in replica that are not in source
    for file_name in os.listdir(replica_folder):
        file_path = os.path.join(replica_folder, file_name)
        if file_name not in source_files:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
                logging.info(f"Removed directory: {file_path}")
            else:
                os.remove(file_path)
                logging.info(f"Removed file: {file_path}")


###########################################################################################
#                                                                                         #
# def periodic_sync(sc, source_folder, replica_folder, log_file, interval)                #
#                                                                                         #
# Function to allow another one (in the present case, the sync_folders one) to run        #
# periodically, with a periodic interval specified                                        #
# Inputs: sc (scheduler object)                                                           #
#         source_folder (path to source folder)                                           #
#         replica_folder (path to replica folder)                                         #
#         log_file (path to log file)                                                     #
#         interval (value of the interval, in seconds, in which the synchronization       #
#                   should be performed)                                                  #
#                                                                                         #
# Author: Solange Santos                                                                  #
# Date: 14/04/2024                                                                        #
#                                                                                         #
###########################################################################################
def periodic_sync(sc, source_folder, replica_folder, log_file, interval):
    sync_folders(source_folder, replica_folder, log_file)
    logging.info("Synchronization complete.")
    sc.enter(interval, 1, periodic_sync, (sc, source_folder, replica_folder, log_file, interval))


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Folder synchronization tool')
    parser.add_argument('source_folder', type=str, help='Path to the source folder')
    parser.add_argument('replica_folder', type=str, help='Path to the replica folder')
    parser.add_argument('log_file', type=str, help='Path to the log file')
    parser.add_argument('sync_interval', type=int, help='Synchronization interval in seconds')
    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_file)

    # Create a scheduler object
    scheduler = sched.scheduler(time.time, time.sleep)

    # Schedule the periodic synchronization
    scheduler.enter(0, 1, periodic_sync, (scheduler, args.source_folder, args.replica_folder, args.log_file, args.sync_interval))

    # Run the scheduler
    scheduler.run()

    print("Folder synchronization completed.")
