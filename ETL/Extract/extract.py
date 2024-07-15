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

def extract_sidecar_data()-> json:
    """
    Function to extract data from all sidecar files from BIDS folder.

    Returns: data (pandas DataFrame): Extracted data from BIDS sidecar files.
    """ 
    ## CHECKS
    # Check if config file is read successfully
    if CONFIG is None:
        workflow_logger.error("Config file not found or not read successfully.")
        exit()
    # Check if extraction should be skipped
    if CONFIG['skip_extraction']:
        workflow_logger.info("Extraction is skipped as per config file.")
        return None
    # Check if extraction path and BIDS directory path exists
    if not os.path.exists(CONFIG['extraction_path']):
        workflow_logger.error(f"Extraction path does not exist: {CONFIG['extraction_path']}")
        exit()
    if not os.path.exists(CONFIG['bids_dir_path']):
        workflow_logger.error(f"BIDS directory path does not exist: {CONFIG['bids_dir_path']}")
        exit()
        
    ## Extract data
    # get BIDS path and check if it exists
    bids_path = os.path.join(CONFIG['bids_dir_path'])
    if not os.path.exists(bids_path):
        workflow_logger.error(f"BIDS path does not exist: {bids_path}")
        exit()
    # Get all sidecar files finding *_sidecar.json
    sidecar_files = Path(bids_path).rglob('*_sidecar.json')

    # Extract data from all sidecar json files
    data = combine_json_files(sidecar_files)
        
    # check if data is empty
    if data is None or len(data) == 0:
        workflow_logger.error("Extracted data is empty, no data will be processed")
        exit()

    ## Store data
    store_data(data)
    workflow_logger.debug(f"Data stored successfully, path: {CONFIG['extraction_path']}/extracted_data.json")
    workflow_logger.info(f"Data extracted:\n{data}")
    return data

def combine_json_files(json_files:list)-> json:
    """
    Combines data from multiple JSON files into a single list.

    :param json_files: List of paths to JSON files
    :return: List containing data from all JSON files
    """
    combined_data = []

    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                combined_data.append(data)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return combined_data

def store_data(data:json) -> None:
    """
    Stores the extracted data into a JSON file.

    :param data: Extracted data to be stored
    :return: None
    """
    # mkdir "data" if not exists
    data_dir = os.path.join(CONFIG['extraction_path'])
    mkdir_if_not_exists(data_dir)
    # Define the path to store the extracted data
    data_file = os.path.join(data_dir, 'extracted_data.json')
    # Check if file already exists
    if os.path.exists(data_file):
        os.remove(data_file)
    # Save extracted data 
    with open(data_file, 'w') as f:
        json.dump(data, f)

# Extract program
if __name__ == "__main__":
    """
    This is the main program that will be executed when the script is run.
    It calls the extract_sidecar_data function to extract data from BIDS sidecar files.
    """
    extracted_data = extract_sidecar_data()
    print(extracted_data)
    workflow_logger.info("Data extracted successfully.")
