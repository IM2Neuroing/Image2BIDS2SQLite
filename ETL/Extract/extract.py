import sys
import os

# Get the current script directory
current_script_directory = os.path.dirname(os.path.realpath(__file__))

# Get the root directory of your repository
root_directory = os.path.abspath(os.path.join(current_script_directory, os.pardir, os.pardir))

# Add the root directory to sys.path
sys.path.append(root_directory)

from PyUtilities import read_config_file, mkdir_if_not_exists

from pathlib import Path
import pandas as pd
import logging

# Configure logger
workflow_logger = logging.getLogger('workflow_logger')

CONFIG_FILE_PATH = 'config.json'
CONFIG = read_config_file(CONFIG_FILE_PATH)

def extract_sidecar_data():
    """
    Function to extract data from all sidecar files from BIDS folder.

    Returns: data (pandas DataFrame): Extracted data from BIDS sidecar files.
    """ 
    # Check if extraction path is provided
    if CONFIG['datasystem_root'] is None or CONFIG['bids_dir_name'] is None:
        workflow_logger.error("BIDS root path or BIDS directory name not provided in config file.")
        exit()

    ## Extract data
    # get BIDS path and check if it exists
    bids_path = os.path.join(CONFIG['datasystem_root'], CONFIG['bids_dir_name'])
    if not os.path.exists(bids_path):
        workflow_logger.error(f"BIDS path does not exist: {bids_path}")
        exit()
    # Get all image files
    image_files = Path(bids_path).rglob('*.nii.gz')
    # Get all sidecar files by replacing image "*.nii.gz" extension with *.json
    sidecar_files = [str(file).replace('.nii.gz', '.json') for file in image_files]

    # Extract data from all sidecar files
    data = pd.DataFrame()
    for file in sidecar_files:
        # Read the sidecar file
        sidecar_data = pd.read_json(file, orient='index').T
        data = pd.concat([data, sidecar_data], ignore_index=True)
        
    # check if data is empty
    if data.empty:
        workflow_logger.error("Extracted data is empty, no data will be processed")
        exit()

    ## Store data
    store_data(data)
    workflow_logger.debug(f"Data stored successfully, path: {CONFIG['datasystem_root']}/SQLiteSetup/data/extracted_data.csv")

    workflow_logger.info(f"Data extracted:\n{data}")
    return data

def store_data(data):
    # mkdir "data" if not exists
    data_dir = os.path.join(CONFIG['datasystem_root'],'SQLiteSetup/data')
    mkdir_if_not_exists(data_dir)

    # Save extracted data to a csv file
    data_file = os.path.join(data_dir, 'extracted_data.csv')
    data.to_csv(data_file, index=False)

# Extract program
if __name__ == "__main__":
    """
    This is the main program that will be executed when the script is run.
    It calls the extract_sidecar_data function to extract data from BIDS sidecar files.
    """
    extracted_data = extract_sidecar_data()
    print(extracted_data)
    workflow_logger.info("Data extracted successfully.")
