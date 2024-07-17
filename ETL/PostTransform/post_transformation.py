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
import json
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
    if not os.path.exists(os.path.join(CONFIG['extraction_path'],'extracted_data.json')):
        workflow_logger.error(f"Extracted data JSON file does not exist: {CONFIG['extraction_path'] + 'extracted_data.json'}")
        exit()

    ## CLEAN IMAGE TABLES
    # Populate Subject IDs in files table
    update_subject_ids()

    # Populate the Transformation_id in the files table
    update_transformation_id()

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
    subjects['BIDS_subject_id'] = subjects["patient_id_acr"].str.replace("-", "").str.replace("_", "").str.strip().str.upper()

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

def update_transformation_id() -> None:
    """
    Function to update the Transformation ID in the files table of SQLite DB.

    return: None
    """
    # Get the Transformation table from the SQLite DB
    engine = create_engine("sqlite:///"+CONFIG["db_path"])  
    with engine.connect() as conn, conn.begin():
        transformations = pd.read_sql_table("transformations", conn)

    # check if the transformations table is empty
    if transformations.empty:
        workflow_logger.error("Transformations table is empty.")
        exit()

    # Get the files table from the SQLite DB
    with engine.connect() as conn, conn.begin():
        files = pd.read_sql_table("files", conn)

    # check if the files table is empty
    if files.empty:
        workflow_logger.error("Files table is empty.")
        exit()

    # USE the extracted data JSON file as dictionary which file has which transformations
    # get the extracted data JSON file
    extracted_data = pd.read_json(os.path.join(CONFIG['extraction_path'],'extracted_data.json'))
    extracted_data.reset_index(drop=False, inplace=True)
    extracted_data.rename(columns={"index":"file_name"}, inplace=True)
    # drop al rows with no "transformations" mentioned in the "sidecardata" column
    extracted_data = extracted_data[extracted_data['sidecardata'].apply(lambda x: 'transformations' in x.keys())]
    # correct file_name column split by "." and take the first element
    extracted_data['file_name'] = extracted_data['file_name'].apply(lambda x: x.split(".")[0].replace("_sidecar", ""))
    # get the transformations_id from the transformations table and add it to the extracted_data table
    extracted_data['transformations'] = extracted_data['sidecardata'].apply(lambda x: x['transformations'])
    extracted_data['transformation_id'] = extracted_data['transformations'].apply(lambda x: transformations[(transformations['identity'] == x['identity']) & (transformations['target_id'] == x['target_id']) & (transformations['transform_id'] == x['transform_id'])]['transformation_id'])

    # add a helper column to get the file name without the extension
    files['file_name'] = files['file_path'].apply(lambda x: os.path.splitext(x)[0].split("/")[-1].split(".")[0])
    # add the transformation_id to the files table
    files['transformation_id'] = files['file_name'].apply(lambda x: extracted_data[extracted_data['file_name'] == x]['transformation_id'].values[0] if not extracted_data[extracted_data['file_name'] == x]['transformation_id'].empty else None)
    # drop the helper column
    files.drop(columns=['file_name'], inplace=True)

    # Update the files table with the transformation_id
    with engine.connect() as conn, conn.begin():
        # Update the files table in the SQLite DB
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
    # Check if SQLite DB path exists
    if not os.path.exists(CONFIG['db_path']):
        workflow_logger.error(f"SQLite DB path does not exist: {CONFIG['db_path']}")
        exit()
        
    ## BACKPROPAGATION
    # Get all _sidecar.json files in the BIDS directory
    sidecar_files = list(Path(CONFIG['bids_dir_path']).rglob('*_sidecar.json'))
    # Check if there are any _sidecar.json files
    if not sidecar_files:
        workflow_logger.error(f"No _sidecar.json files found in {CONFIG['bids_dir_path']}")
        exit()
    
    # Get the files table from the SQLite DB
    engine = create_engine("sqlite:///"+CONFIG["db_path"])
    with engine.connect() as conn, conn.begin():
        files = pd.read_sql_table("files", conn)

    # check if the files table is empty
    if files.empty:
        workflow_logger.error("Files table is empty.")
        exit()
    
    # Get the bids table from the SQLite DB
    with engine.connect() as conn, conn.begin():
        bids = pd.read_sql_table("bids", conn)

    # check if the bids table is empty
    if bids.empty:
        workflow_logger.error("Bids table is empty.")
        exit()
    
    # Get the labels table from the SQLite DB
    with engine.connect() as conn, conn.begin():
        labels = pd.read_sql_table("labels", conn)
    
    # check if the labels table is empty
    if labels.empty:
        workflow_logger.error("Labels table is empty.")
        exit()
    
    # Get the transformations table from the SQLite DB
    with engine.connect() as conn, conn.begin():
        transformations = pd.read_sql_table("transformations", conn)
    
    # check if the transformations table is empty
    if transformations.empty:
        workflow_logger.error("Transformations table is empty.")
        exit()
    

    # Loop through all the _sidecar.json files
    for sidecar_file in sidecar_files:
        # open sidecar file
        with open(sidecar_file) as f:
            sidecar_json = json.load(f)

        # check wheter the sidecar file contains the key "files"
        if "files" in sidecar_json.keys():
            file = sidecar_json["files"]
            # update the json "file" according to the row in files table of sqlite db
            # get the file_id from the json file
            file_id = file["file_id"]
            # get the row in the files table with the file_id
            file_row = files[files["file_id"] == file_id]
            # update the file json replace null or Nan with ""
            file["subject_id"] = str(file_row["subject_id"].values[0]).replace("null", "").replace("nan", "")
            file["electrode_id"] = str(file_row["electrode_id"].values[0]).replace("null", "").replace("nan", "")
            file["file_path"] = str(file_row["file_path"].values[0]).replace("null", "").replace("nan", "")
            file["file_type"] = str(file_row["file_type"].values[0]).replace("null", "").replace("nan", "")
            file["source_id"] = str(file_row["source_id"].values[0]).replace("null", "").replace("nan", "")

            sidecar_json["files"] = file

            # check wheter the sidecar file contains the key "bids"
            if "bids" in sidecar_json.keys():
                bid = sidecar_json["bids"]
                # update the json "bids" according to the row in bids table of sqlite db
                # get the row in the bids table with the file_id
                bid_row = bids[bids["file_id"] == file_id]
                # update the bids json 
                bid["modality"] = str(bid_row["modality"].values[0]).replace("null", "").replace("nan", "")
                bid["protocol_name"] = str(bid_row["protocol_name"].values[0]).replace("null", "").replace("nan", "")
                bid["stereotactic"] = str(bid_row["stereotactic"].values[0]).replace("null", "").replace("nan", "")
                bid["dicom_image_type"] = str(bid_row["dicom_image_type"].values[0]).replace("null", "").replace("nan", "")
                bid["acquisition_date_time"] = str(bid_row["acquisition_date_time"].values[0]).replace("null", "").replace("nan", "")
                bid["relative_sidecar_path"] = str(bid_row["relative_sidecar_path"].values[0]).replace("null", "").replace("nan", "")
                bid["bids_subject"] = str(bid_row["bids_subject"].values[0]).replace("null", "").replace("nan", "")
                bid["bids_session"] = str(bid_row["bids_session"].values[0]).replace("null", "").replace("nan", "")
                bid["bids_extension"] = str(bid_row["bids_extension"].values[0]).replace("null", "").replace("nan", "")
                bid["bids_datatype"] = str(bid_row["bids_datatype"].values[0]).replace("null", "").replace("nan", "")
                bid["bids_acquisition"] = str(bid_row["bids_acquisition"].values[0]).replace("null", "").replace("nan", "")
                bid["bids_suffix"] = str(bid_row["bids_suffix"].values[0]).replace("null", "").replace("nan", "")

                sidecar_json["bids"] = bid

            # check wheter the sidecar file contains the key "labels"
            if "labels" in sidecar_json.keys():
                label = sidecar_json["labels"]
                # update the json "labels" according to the row in labels table of sqlite db
                # get the row in the labels table with the file_id
                label_row = labels[labels["file_id"] == file_id]
                # update the labels json
                label["hemisphere"] = str(label_row["hemisphere"].values[0]).replace("null", "").replace("nan", "")
                label["structure"] = str(label_row["structure"].values[0]).replace("null", "").replace("nan", "")
                label["color"] = str(label_row["color"].values[0]).replace("null", "").replace("nan", "")
                label["comment"] = str(label_row["comment"].values[0]).replace("null", "").replace("nan", "")

                sidecar_json["labels"] = label
                
            # check wheter the sidecar file contains the key "transformations"
            if "transformations" in sidecar_json.keys():
                transformation = sidecar_json["transformations"]
                # update the json "transformations" according to the row in transformations table of sqlite db
                # get the row in the transformations table with the identity, target_id, transform_id
                transformation_row = transformations[(transformations["identity"] == transformation["identity"]) & (transformations["target_id"] == transformation["target_id"]) & (transformations["transform_id"] == transformation["transform_id"])]
                # update the transformations json
                transformation["transformation_id"] = str(transformation_row["transformation_id"].values[0]).replace("null", "").replace("nan", "")
                transformation["identity"] = str(transformation_row["identity"].values[0]).replace("null", "").replace("nan", "")
                transformation["target_id"] = str(transformation_row["target_id"].values[0]).replace("null", "").replace("nan", "")
                transformation["transform_id"] = str(transformation_row["transform_id"].values[0]).replace("null", "").replace("nan", "")
                
                sidecar_json["transformations"] = transformation
            
            # write the updated sidecar file
            with open(sidecar_file, 'w') as f:
                json.dump(sidecar_json, f, indent=4)

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
    backpropation()
    workflow_logger.info("Data successfully backpropagated.")
