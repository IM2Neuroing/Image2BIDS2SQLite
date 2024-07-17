import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))

from PyUtilities import read_config_file, calculate_hash
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

    # create sidecar files for the Slicer files
    create_sidecar_files()

def create_sidecar_files():
    """
    Create sidecar files for the Slicer files
    Sidecar files are json files that contain metadata information about the data files

    files_info = {  "file_id": file_id,
                    "subject_id" : patientconfig['record_id'],
                    "file_path" : bids_file_path,
                    "file_type" : "segmentation",
                    "file_origin": nifti_file_path
                    "modality": "MR",
                    "protocol_name": "WAIR",
                    "stereotactic": None,
                    "dicom_image_type": "BRAINLAB",
                    "bids_subject": patientconfig['bids_id'],
                    "bids_session": "Pre",
                    "bids_extension": "nii.gz",
                    "bids_datatype": "segmentation",
                    "bids_acquisition": "MR-WAIR-"+nifti_file_region,
                    "bids_suffix": "label"
                    "hemisphere": nifti_file_name.split("_")[0],
                    "structure": "-".join(nifti_file_name.split("_")[1:])
                    }
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
        
        # create the BIDSLayout object
        layout = BIDSLayout(bids_root_dir)

        # get the list of files in the derivatives directory
        files = os.listdir(derivatives_slicer_dir)

        # Iterate over all files in the derivatives directory
        for file in files:
            # get the file path
            file_path_abs = os.path.join(derivatives_slicer_dir, file)
            # check file type
            file_seg_1 = file.split("_")[0]
            # check file type
            if file_seg_1 in ["MR", "DTI", "T1", "T2", "WAIR"]:
                file_info = getMRFileInfo(file_path_abs, file, patientconfig)
            elif file_seg_1 in ["CT"]:
                file_info = getCTFileInfo(file_path_abs, file, patientconfig)
            elif file_seg_1 in ["L","R"] and file.split(".")[-2:-1] == "seg.nrrd":
                file_info = getSegmentationFileInfo(file_path_abs, file, patientconfig)
            elif file.split(".")[-2:-1] == "mrk.json":
                file_info = getMrkFileInfo(file_path_abs, file, patientconfig)
            else:
                workflow_logger.error(f"File {file} is not recognized")
                continue

            # write the file info to the sidecar file
            sidecar_file_path_abs = file_path_abs.split(".")[0:-1]+".sidecar.json"
            with open(sidecar_file_path_abs, 'w') as f:
                json.dump(file_info, f)
            workflow_logger.info(f"Created sidecar file {sidecar_file_path_abs}")
            
def getMRFileInfo(file_path_abs, file, patientconfig):
    """
    Get metadata information for MR files
    """
    # correct file_path only until BIDS root directory for storage in the database
    file_path = os.path.join(CONFIG["bids_dir_name"],file_path_abs.split(CONFIG["bids_dir_name"])[1])

    # get the file sequence
    file_sequence = file.split("_")[1]
    if file_sequence == "DTI":
        file_sequence_number = file.split("_")[2]
        if file_sequence_number not in ["stereo","nonstereo"]:
            file_sequence = f"{file_sequence}{file_sequence_number}"
            file_stereo = file.split("_")[3]
        # get the file stereo
        else:
            file_stereo = file.split("_")[2]
    else:
        # get the file stereo
        file_stereo = file.split("_")[2]
    # get the file pre/post
    file_prepost = file.split("_")[-1].capitalize().split(".")[0]

    # create the file info dictionary
    file_info = {  "file_id": calculate_hash(file_path_abs),
                    "subject_id" : patientconfig['record_id'],
                    "file_path" : file_path,
                    "file_type" : "3DSlicer",
                    "file_origin": None,
                    "modality": "MR",
                    "protocol_name": file_sequence,
                    "stereotactic": file_stereo,
                    "dicom_image_type": None,
                    "bids_subject": patientconfig['bids_id'],
                    "bids_session": file_prepost,
                    "bids_extension": None,
                    "bids_datatype": None,
                    "bids_acquisition": None,
                    "bids_suffix": None,
                    }
    return file_info

def getCTFileInfo(file_path_abs, file, patientconfig):
    """
    Get metadata information for CT files
    """
    # correct file_path only until BIDS root directory for storage in the database
    file_path = os.path.join(CONFIG["bids_dir_name"],file_path_abs.split(CONFIG["bids_dir_name"])[1])

    # get the file stereo
    file_stereo = file.split("_")[1]
    # get the file pre/post
    file_prepost = file.split("_")[-1].capitalize().split(".")[0]

    # create the file info dictionary
    file_info = {  "file_id": calculate_hash(file_path_abs),
                    "subject_id" : patientconfig['record_id'],
                    "file_path" : file_path,
                    "file_type" : "3DSlicer",
                    "file_origin": None,
                    "modality": "CT",
                    "protocol_name": None,
                    "stereotactic": file_stereo,
                    "dicom_image_type": None,
                    "bids_subject": patientconfig['bids_id'],
                    "bids_session": file_prepost,
                    "bids_extension": None,
                    "bids_datatype": None,
                    "bids_acquisition": None,
                    "bids_suffix": None,
                    }
    return file_info

def getSegmentationFileInfo(file_path_abs, file, patientconfig):
    """
    Get metadata information for Segmentation files
    """
    # correct file_path only until BIDS root directory for storage in the database
    file_path = os.path.join(CONFIG["bids_dir_name"],file_path_abs.split(CONFIG["bids_dir_name"])[1])

    # get the file region
    file_region = file.split("_")[1]

    # create the file info dictionary
    file_info = {  "file_id": calculate_hash(file_path_abs),
                    "subject_id" : patientconfig['record_id'],
                    "file_path" : file_path,
                    "file_type" : "3DSlicer",
                    "file_origin": None,
                    "modality": "MR",
                    "protocol_name": "WAIR",
                    "stereotactic": None,
                    "dicom_image_type": None,
                    "bids_subject": patientconfig['bids_id'],
                    "bids_session": "PRE",
                    "bids_extension": "seg.nrrd",
                    "bids_datatype": "segmentation",
                    "bids_acquisition": "MRWAIR"+file_region,
                    "bids_suffix": "label",
                    "hemisphere": file.split("_")[0],
                    "structure": file.split("_")[1:].split(".")[0]
                    }
    return file_info

def getMrkFileInfo(file_path_abs, file, patientconfig):
    """
    Get metadata information for MRK files
    """
    # correct file_path only until BIDS root directory for storage in the database
    file_path = os.path.join(CONFIG["bids_dir_name"],file_path_abs.split(CONFIG["bids_dir_name"])[1])

    # get the file region
    file_region = file.split("_")[1]

    # create the file info dictionary
    file_info = {  "file_id": calculate_hash(file_path_abs),
                    "subject_id" : patientconfig['record_id'],
                    "file_path" : file_path,
                    "file_type" : "3DSlicer",
                    "file_origin": None,
                    "modality": None,
                    "protocol_name": None,
                    "stereotactic": None,
                    "dicom_image_type": None,
                    "bids_subject": patientconfig['bids_id'],
                    "bids_session": None,
                    "bids_extension": "mrk.json",
                    "bids_datatype": "Trajectory",
                    "bids_acquisition": file_region,
                    "bids_suffix": "label",
                    "hemisphere": file.split("_")[0],
                    "structure": file.split("_")[1:].split(".")[0]
                    }
    return file_info

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