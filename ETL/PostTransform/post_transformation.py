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
from sqlalchemy import create_engine 

# Configure logger
workflow_logger = logging.getLogger('workflow_logger')

CONFIG_FILE_PATH = 'config.json'
CONFIG = read_config_file(CONFIG_FILE_PATH)

def clean_image_tables() -> None:
    """
    Function to clean and update the Image tables of SQLite DB.

    return: None
    """
    ## CHECKS
    # Check if config file is read successfully
    if CONFIG is None:
        workflow_logger.error("Config file not found or not read successfully.")
        exit()
    # Check if image cleaning should be skipped
    if CONFIG['skip_image_cleaning']:
        workflow_logger.info("Image cleaning is skipped as per config file.")
        exit()
    # Check if SQLite DB path exists
    if not os.path.exists(CONFIG['db_path']):
        workflow_logger.error(f"SQLite DB path does not exist: {CONFIG['db_path']}")
        exit()
    # Check if extraction path exists
    if not os.path.exists(CONFIG['extraction_path']):
        workflow_logger.error(f"Extracted data file path does not exist: {CONFIG['extraction_path']}")
        exit()
    # Check if the extracted data JSON file exists
    if not os.path.exists(CONFIG['extraction_path'] + 'extracted_data.json'):
        workflow_logger.error(f"Extracted data JSON file does not exist: {CONFIG['extraction_path'] + 'extracted_data.json'}")
        exit()

    ## CLEAN IMAGE TABLES
    # Populate Subject IDs in files table
    update_subject_ids()

    # Populate the Transformation_id in the files table
    # update_transformation_id()

def update_subject_ids() -> None:
    """
    Function to update the Subject IDs in the files table of SQLite DB.

    return: None
    """  
    # Get the Subjects table from the SQLite DB
    engine = create_engine("sqlite:///"+CONFIG["db_path"])  
    with engine.connect() as conn, conn.begin():
        subjects = pd.read_sql_table("subjects", conn)

    # check if the subjects table is empty
    if subjects.empty:
        workflow_logger.error("Subjects table is empty.")
        exit()
    
    # Create a column for BIDS subject ID
    subjects['BIDS_subject_id'] = subjects["patient_id_acr"].str.replace("-", "").str.replace("_", "").str.upper()

    # Update the files table with the BIDS subject ID
    # get the files table
    with engine.connect() as conn, conn.begin():
        files = pd.read_sql_table("files", conn)
    # check if the files table is empty
    if files.empty:
        workflow_logger.error("Files table is empty.")
        exit()
       
    # create a new column for BIDS subject ID
    files['BIDS_subject_id'] = files['file_path'].apply(lambda x: x.split("/")[-1].split("_")[0].replace("sub-", "").strip().upper())
    # Add the real subject ID to the files table
    files['subject_id'] = files['BIDS_subject_id'].apply(lambda x: subjects[subjects['BIDS_subject_id'] == x]['subject_id'].values[0] if not subjects[subjects['BIDS_subject_id'] == x]['subject_id'].empty else None)
    # Drop BIDS_subject_id column
    files.drop(columns=['BIDS_subject_id'], inplace=True)
    
    # Update the files table in the SQLite DB
    with engine.connect() as conn, conn.begin():
        files.to_sql("files", conn, if_exists='replace', index=False)


def backpropation()-> None:
    """
    Function to backpropagate the loaded data to the BIDS sidecar files.
    """ 
    ## CHECKS
    # Check if config file is read successfully
    if CONFIG is None:
        workflow_logger.error("Config file not found or not read successfully.")
        exit()
    # Check if backpropagation should be skipped
    if CONFIG['skip_backpropagation']:
        workflow_logger.info("Backpropagation is skipped as per config file.")
        return None
    # Check if BIDS directory path exists
    if not os.path.exists(CONFIG['bids_dir_path']):
        workflow_logger.error(f"BIDS directory path does not exist: {CONFIG['bids_dir_path']}")
        exit()
        
    ## BACKPROPAGATION
    # Get the list of all the BIDS subject directories
    exit()

# Post Transformation program
if __name__ == "__main__":
    """
    This is the main program that will be executed when the script is run.
    It calls the functions to clean the Image tables of SQLite DB and update BIDS sidecar files.
    """
    # Call clean Image tables function
    clean_image_tables()
    workflow_logger.info("Image tables cleaned successfully.")

    # Call backpropagation function
    # backpropation()
    # workflow_logger.info("Data successfully backpropagated.")
