import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))

from PyUtilities import read_config_file, mkdir_if_not_exists
import logging
import pandas as pd
import os
import shutil
from bids import BIDSLayout

# Configure logger
workflow_logger = logging.getLogger('workflow_logger')
workflow_logger.setLevel(logging.INFO)
file_handler1 = logging.FileHandler('workflow.log')
formatter = logging.Formatter('%(asctime)-20s - %(levelname)-10s - %(filename)-25s - %(funcName)-25s %(message)-50s')
file_handler1.setFormatter(formatter)
workflow_logger.addHandler(file_handler1)

# Read the configuration file
CONFIG_FILE_PATH = 'config.json'
CONFIG = read_config_file(CONFIG_FILE_PATH)

# Main Workflow
def sclicer_bids_integration():
    """
    Main workflow to import and rename Slicer scenes and files to existing BIDS format
    """
    # Import the Slicer files to BIDS
    cp_slicer_files_to_bids()

    # Rename the files to BIDS format
    rename_files_to_bids()

    # update scene text files to work with BIDS file names
    update_scene_files()

def update_scene_files():
    pass

def rename_files_to_bids():
    """
    Rename the files to BIDS format
    """
    # define directory paths
    bids_root_dir = CONFIG['datasystem_root']+CONFIG['bids_dir_name']
    derivatives_dir = os.path.join(bids_root_dir, 'derivatives','Patients')
    # read export info file to get the subject information
    participants = pd.read_csv(os.path.join(bids_root_dir, "participants.tsv"), sep="\t")

    # Iterate over all Patients
    workflow_logger.info("Iterating over all patients")
    for patient_idx in range(len(participants)):
        # select the patient
        patientconfig = participants.iloc[patient_idx]
        workflow_logger.info(f"Processing patient {patientconfig['bids_id']}")

        # get the slicer subject directory and the derivatives directory
        derivatives_slicer_dir = os.path.join(derivatives_dir,f"sub-{patientconfig['bids_id']}", "3DSlicer")

        # check if the derivatives directory exists
        if not os.path.exists(derivatives_slicer_dir):
            workflow_logger.error(f"Derivatives directory {derivatives_slicer_dir} does not exist")
            continue

        # create a pandas dataframe to store the file name mapping
        file_mapping = pd.DataFrame(columns=['old_file_name', 'new_file_name'])

        # get the list of files in the directory
        files = os.listdir(derivatives_slicer_dir)
        # iterate over all files
        for file in files:
            # get the file path
            file_path = os.path.join(derivatives_slicer_dir, file)
            # get the file extension
            file_ext = os.path.splitext(file)[-1]
            # get the file name without extension
            file_name = os.path.splitext(file)[0]

def cp_slicer_files_to_bids():
    """
    Copy Slicer files to BIDS directory
    """
    # define directory paths
    bids_root_dir = CONFIG['datasystem_root']+CONFIG['bids_dir_name']
    slicer_scene_root_dir = os.path.join(CONFIG["datasystem_root"], CONFIG["slicer_dir_name"])
    derivatives_dir = os.path.join(bids_root_dir, 'derivatives','Patients')

    # read export info file to get the subject information
    participants = pd.read_csv(os.path.join(bids_root_dir, "participants.tsv"), sep="\t")

    # Iterate over all Patients
    workflow_logger.info("Iterating over all patients")
    for patient_idx in range(len(participants)):
        # select the patient
        patientconfig = participants.iloc[patient_idx]
        workflow_logger.info(f"Processing patient {patientconfig['bids_id']}")

        # get the slicer subject directory and the derivatives directory
        derivatives_slicer_dir = os.path.join(derivatives_dir,f"sub-{patientconfig['bids_id']}", "3DSlicer")
        # mkdir_if_not_exists(derivatives_slicer_dir)
        subject_slicer_dir = os.path.join(slicer_scene_root_dir, patientconfig['folder_name'])

        # check if the slicer directory exists
        if not os.path.exists(subject_slicer_dir):
            workflow_logger.error(f"Slicer directory {subject_slicer_dir} does not exist")
            continue
        # check if the derivatives directory exists
        if os.path.exists(derivatives_slicer_dir):
            workflow_logger.error(f"Derivatives directory {derivatives_slicer_dir} already exists")
            continue
        # copy the slicer files to the derivatives directory
        shutil.copytree(subject_slicer_dir, derivatives_slicer_dir)
        workflow_logger.info(f"Copied Slicer files from {subject_slicer_dir} to {derivatives_slicer_dir}")

# Main program
if __name__ == "__main__":
    """
    Main workflow to import and rename Slicer scenes and files to existing BIDS format
    """
    sclicer_bids_integration()