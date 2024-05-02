from PyUtilities.setupFunctions import read_config_file
from PyUtilities.edit_add_bids_templates import copy_templates_to_bids_root, add_participants_ids_to_tsv, change_dataset_name
from PyUtilities.utility_functions import mkdir_if_not_exists, calculate_hash
import logging
import pandas as pd
import os
import shutil
from bids import BIDSLayout

# Configure logger
workflow_logger = logging.getLogger('workflow_logger')
workflow_logger.setLevel(logging.INFO)
file_handler1 = logging.FileHandler('Workflow-debug.log')
formatter = logging.Formatter('%(asctime)-20s - %(levelname)-10s - %(filename)-25s - %(funcName)-25s %(message)-50s')
file_handler1.setFormatter(formatter)
workflow_logger.addHandler(file_handler1)

# Configure logger
# workflow_logger = logging.getLogger('workflow_logger')

CONFIG_FILE_PATH = 'config.json'
CONFIG = read_config_file(CONFIG_FILE_PATH)

def get_datatype_name(file_name):
    """
    Datatypes are set according to the documentation in obsidian
    `Work_General/BIDS/22_11 Creating our BIDS folder hierarchy`
    -> 'anat: T1, T2, WAIR, CT'
    -> 'dwi:DTI, DPTSE'
    :param in_str:
    :return:
    """
    # get the file_name description
    file_name = file_name.lower()

    # check if the series is a anatomical image
    # 'anat: T1, T2, WAIR, CT'
    anatlist = ['t1', 't2', 'wair', 'ct']
    if any(x in file_name for x in anatlist):
        return "anat"
    # check if the series is a diffusion weighted image
    # 'dwi:DTI, DPTSE'
    dwilist = ['dti', 'dptse']
    if any(x in file_name for x in dwilist):
        return "dwi"
    return "anat"
    
def get_suffix_name(sequence):
    """
    Suffixes are set according to the documentation in obsidian
    `Work_General/BIDS/22_11 Creating our BIDS folder hierarchy`
    -> T1 = T1w, T2 = T2w, DTI = dwi, WAIR = FLAIR, CT = T2star, other = notDefinedInScript
    :param in_str:
    :return:
    """
    # get the series description
    sequence = sequence.upper()

    suffix_mappings = {
            'T1': 'T1w',
            'T2': 'T2w',
            'B0' : 'dwi',
            'DTI': 'dwi',
            'WAIR': 'FLAIR',
            'CT': 'T2star',
            'DPTSE': 'dwi'
        }
    
    suffix = suffix_mappings.get(sequence, 'notDefinedInScript')
    # if the suffix is not defined in the mappings log a warning
    if suffix == 'notDefinedInScript':
        logging.warning(f"Suffix for sequence {sequence} is not defined in the mappings.")
    return suffix

# create image functions
def create_bids_mr_image(nifti_file_path, nifti_file_name, subject_dir, patientconfig):
    # get the file sequence
    nifti_file_sequence = nifti_file_name.split("_")[1]
    if nifti_file_sequence == "DTI":
        nifti_file_sequence_number = nifti_file_name.split("_")[-1]
        nifti_file_sequence = f"{nifti_file_sequence}-{nifti_file_sequence_number}"
    # get the file stereo
    nifti_file_stereo = nifti_file_name.split("_")[2]
    # get the file pre/post
    try:
        nifti_file_prepost = nifti_file_name.split("_")[3].capitalize()
    except:
        nifti_file_prepost = "pre"
    

    # create the corresponding directories
    # create the BIDS session directory
    session_dir = os.path.join(subject_dir,f'ses-{nifti_file_prepost}')
    mkdir_if_not_exists(session_dir)
    # get the datatype
    datatype = get_datatype_name(nifti_file_sequence)
    # create the BIDS datatype directory
    datatype_dir = os.path.join(session_dir, datatype)
    mkdir_if_not_exists(datatype_dir)
    # create the BIDS file name
    bids_file_name = f"sub-{patientconfig['bids_id']}_ses-{nifti_file_prepost}_acq-mr{nifti_file_sequence}_{get_suffix_name(nifti_file_sequence)}.nii.gz"
    # create the BIDS file path
    bids_file_path = os.path.join(datatype_dir, bids_file_name)
    # copy the NIFTI file to the BIDS directory
    shutil.copy2(nifti_file_path, bids_file_path)

    #Preparation for the dictionary
    file_id = calculate_hash(bids_file_path)

    # define dictionary to store the files,bids infos
    files_info = {  "file_id": file_id,
                    "subject_id" : patientconfig['record_id'],
                    "file_path" : bids_file_path,
                    "file_type" : "raw-image",
                    "file_origin": nifti_file_path
                    }
    bids_info = { "file_id": file_id,
                    "modality": "MR",
                    "protocol_name": nifti_file_sequence,
                    "stereotactic": nifti_file_stereo,
                    "dicom_image_type": "BRAINLAB",
                    "bids_subject": patientconfig['bids_id'],
                    "bids_session": nifti_file_prepost,
                    "bids_extension": "nii.gz",
                    "bids_datatype": datatype,
                    "bids_acquisition": "MR-"+nifti_file_sequence,
                    "bids_suffix": get_suffix_name(nifti_file_sequence)
                    }
    # create a json sidecar file
    # create the BIDS sidecar file name
    bids_sidecar_name = f"sub-{patientconfig['bids_id']}_ses-{nifti_file_prepost}_acq-mr{nifti_file_sequence}_{get_suffix_name(nifti_file_sequence)}.json"
    # create the BIDS sidecar file path
    bids_sidecar_path = os.path.join(datatype_dir, bids_sidecar_name)
    # create the sidecar file with content from the dataframes
    with open(bids_sidecar_path, 'w') as f:
        f.write("{\n")
        for key, value in files_info.items():
            f.write(f'"{key}": "{value}",\n')
        for key, value in bids_info.items():
            f.write(f'"{key}": "{value}",\n')
        # remove the last comma
        f.seek(f.tell()-2)
        f.write("\n}")
    return files_info, bids_info


def create_bids_ct_image(nifti_file_path, nifti_file_name, subject_dir, patientconfig):
    # get the file stereo
    nifti_file_stereo = nifti_file_name.split("_")[1]
    # get the file pre/post
    nifti_file_prepost = nifti_file_name.split("_")[2].capitalize()

    # create the corresponding directories
    # create the BIDS session directory
    session_dir = os.path.join(subject_dir,f'ses-{nifti_file_prepost}')
    mkdir_if_not_exists(session_dir)
    # get the datatype
    datatype = get_datatype_name("CT")
    # create the BIDS datatype directory
    datatype_dir = os.path.join(session_dir, datatype)
    mkdir_if_not_exists(datatype_dir)
    # create the BIDS file name
    bids_file_name = f"sub-{patientconfig['bids_id']}_ses-{nifti_file_prepost}_acq-CT_{get_suffix_name('CT')}.nii.gz"
    # create the BIDS file path
    bids_file_path = os.path.join(datatype_dir, bids_file_name)
    # copy the NIFTI file to the BIDS directory
    shutil.copy2(nifti_file_path, bids_file_path)

    #Preparation for the dictionary
    file_id = calculate_hash(bids_file_path)

    # define dictionary to store the files,bids infos
    files_info = {  "file_id": file_id,
                    "subject_id" : patientconfig['record_id'],
                    "file_path" : bids_file_path,
                    "file_type" : "raw-image",
                    "file_origin": nifti_file_path
                    }
    bids_info = { "file_id": file_id,
                    "modality": "CT",
                    "protocol_name": "",
                    "stereotactic": nifti_file_stereo,
                    "dicom_image_type": "BRAINLAB",
                    "bids_subject": patientconfig['bids_id'],
                    "bids_session": nifti_file_prepost,
                    "bids_extension": "nii.gz",
                    "bids_datatype": datatype,
                    "bids_acquisition": "CT",
                    "bids_suffix": get_suffix_name('CT')
                    }
    # create a json sidecar file
    # create the BIDS sidecar file name
    bids_sidecar_name = f"sub-{patientconfig['bids_id']}_ses-{nifti_file_prepost}_acq-CT_{get_suffix_name('CT')}.json"
    # create the BIDS sidecar file path
    bids_sidecar_path = os.path.join(datatype_dir, bids_sidecar_name)
    # create the sidecar file with content from the dataframes
    with open(bids_sidecar_path, 'w') as f:
        f.write("{\n")
        for key, value in files_info.items():
            f.write(f'"{key}": "{value}",\n')
        for key, value in bids_info.items():
            f.write(f'"{key}": "{value}",\n')
        # remove the last comma
        f.seek(f.tell()-2)
        f.write("\n}")
    return files_info, bids_info
    

def create_bids_label_image(nifti_file_path, nifti_file_name, subject_dir, patientconfig):
    # get the file region
    # replace _ with - in the region name | e.g. 'hippocampus_left'->'hippocampus-left'
    nifti_file_region = "-".join(nifti_file_name.split("_"))
    # create the BIDS datatype directory
    datatype_dir = os.path.join(subject_dir, "Segmentations")
    mkdir_if_not_exists(datatype_dir)
    # create the BIDS file name
    bids_file_name = f"sub-{patientconfig['bids_id']}_ses-Pre_acq-mrWair{nifti_file_region}_label.nii.gz"
    # create the BIDS file path
    bids_file_path = os.path.join(datatype_dir, bids_file_name)
    # copy the NIFTI file to the BIDS directory
    shutil.copy2(nifti_file_path, bids_file_path)
    file_id = calculate_hash(bids_file_path)

    # define dictionary to store the files,bids infos
    files_info = {  "file_id": file_id,
                    "subject_id" : patientconfig['record_id'],
                    "file_path" : bids_file_path,
                    "file_type" : "segmentation",
                    "file_origin": nifti_file_path
                    }
    bids_info = { "file_id": file_id,
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
                    }
    labels_info = { "file_id": file_id,    
                    "hemisphere": nifti_file_name.split("_")[0],
                    "structure": "-".join(nifti_file_name.split("_")[1:])
                    }
    # create a json sidecar file
    # create the BIDS sidecar file name
    bids_sidecar_name = f"sub-{patientconfig['bids_id']}_ses-Pre_acq-mrWair{nifti_file_region}_label.json"
    # create the BIDS sidecar file path
    bids_sidecar_path = os.path.join(datatype_dir, bids_sidecar_name)
    # create the sidecar file with content from the dataframes
    with open(bids_sidecar_path, 'w') as f:
        f.write("{\n")
        for key, value in files_info.items():
            f.write(f'"{key}": "{value}",\n')
        for key, value in bids_info.items():
            f.write(f'"{key}": "{value}",\n')
        for key, value in labels_info.items():
            f.write(f'"{key}": "{value}",\n')
        # remove the last comma
        f.seek(f.tell()-2)
        f.write("\n}")
    return files_info, bids_info , labels_info

# Main Workflow
def NIFTI2BIDS():
    """
    Main workflow to convert NIFTI files to BIDS format
    """
    ## INITIALIZE empty BIDS datastructure
    # define directory paths
    repository_root_dir = CONFIG['repository_root']
    bids_root_dir = CONFIG['datasystem_root']+CONFIG['bids_dir_name']
    forbids_root_dir = os.path.join(CONFIG["datasystem_root"], CONFIG["4bids_dir_name"])
    # define default data from CONFIG file

    templ_participants_json = "BIDS/bids_templates/participants.json"
    templ_readme = "BIDS/bids_templates/README.MD"
    templ_dataset_description = "BIDS/bids_templates/dataset_description_raw.json"

    # read export info file to get the subject information
    exportinfo_path = os.path.join(forbids_root_dir,"export_info.json")
    subjects = pd.read_json(exportinfo_path)

    # create column bids_id without - or _ and all capital letters
    subjects["bids_id"] = subjects["patient_id"].str.replace("-", "").str.replace("_", "").str.upper()

    # create column participant_id
    subjects["participant_id"] = subjects["patient_id"].str.upper()

    # create the BIDS root and derivatives dir and Patients dir (if not exists)
    mkdir_if_not_exists(bids_root_dir)
    derivatives_dir = os.path.join(bids_root_dir, 'derivatives')
    mkdir_if_not_exists(derivatives_dir)
    derivatives_patients_dir = os.path.join(derivatives_dir, 'Patients')
    mkdir_if_not_exists(derivatives_patients_dir)

    # get default configuration files from repository
    # copy the templates: README, dataset_description, participants.json
    copy_templates_to_bids_root(
        os.path.join(repository_root_dir, templ_readme),
        os.path.join(repository_root_dir, templ_dataset_description),
        os.path.join(repository_root_dir, templ_participants_json),
        bids_root_dir
    )
    # Fill the description.json
    # set the root directory name as the dataset name in description.json
    change_dataset_name(bids_root_dir)

    # Fill the participants.tsv
    # add the participant ids to the participants tsv
    participants_df = add_participants_ids_to_tsv(bids_root_dir, subjects)

    # create a dataframe with all columns for the BIDS info
    files_info_df = pd.DataFrame(columns=["file_id", "subject_id","file_path", "file_type", "file_origin"])
    bids_info_df = pd.DataFrame(columns=["file_id", "modality", "protocol_name", "stereotactic", "dicom_image_type", "bids_subject", "bids_session", "bids_extension", "bids_datatype","bids_acquisition","bids_suffix"])
    labels_info_df = pd.DataFrame(columns=["file_id", "hemisphere","structure"])

    # Iterate over all Patients
    workflow_logger.info("Iterating over all patients")
    for patient_idx in range(len(subjects)):
        # select the patient
        patientconfig = subjects.iloc[patient_idx]
        # create the subject BIDS directory and the derivatives directory
        subject_dir = os.path.join(bids_root_dir, f"sub-{patientconfig['bids_id']}")
        mkdir_if_not_exists(subject_dir)
        derivatives_subject_dir = os.path.join(derivatives_patients_dir,f"sub-{patientconfig['bids_id']}")
        mkdir_if_not_exists(derivatives_subject_dir)

        # get the subject NIFTI directory
        subject_nifti_dir = os.path.join(forbids_root_dir, patientconfig['folder_name'])
        image_idx = 0
        # iterate over all the NIFTI files in subject NIFTI directory
        for nifti_file in os.listdir(subject_nifti_dir):
            # increment the image index
            image_idx += 1
            # get the full path of the NIFTI file
            nifti_file_path = os.path.join(subject_nifti_dir, nifti_file)
            # get the file name
            nifti_file_name = os.path.splitext(nifti_file)[0].split(".")[0]

            # get the file type
            nifti_file_type = nifti_file_name.split("_")[0]

            # check if the file type is a MR, CT or Label    
            if nifti_file_type == "MR":
                #create MR image in BIDS format
                file_info_dict, bids_info_dict = create_bids_mr_image(nifti_file_path, nifti_file_name, subject_dir, patientconfig)
                # append the file info to the files_info_df
                files_info_df = pd.concat([files_info_df, pd.DataFrame(file_info_dict, index=[image_idx])], ignore_index=True)
                # append the bids info to the bids_info_df
                bids_info_df = pd.concat([bids_info_df, pd.DataFrame(bids_info_dict, index=[image_idx])], ignore_index=True)

            elif nifti_file_type == "CT":
                # create CT image in BIDS format
                file_info_dict, bids_info_dict = create_bids_ct_image(nifti_file_path, nifti_file_name, subject_dir, patientconfig)
                # append the file info to the files_info_df
                files_info_df = pd.concat([files_info_df, pd.DataFrame(file_info_dict, index=[image_idx])], ignore_index=True)
                # append the bids info to the bids_info_df
                bids_info_df = pd.concat([bids_info_df, pd.DataFrame(bids_info_dict, index=[image_idx])], ignore_index=True)
            elif nifti_file_type in ["R", "L"]:
                # create Label image in BIDS format
                file_info_dict, bids_info_dict, label_info_dict = create_bids_label_image(nifti_file_path, nifti_file_name, derivatives_subject_dir, patientconfig)
                # append the file info to the files_info_df
                files_info_df = pd.concat([files_info_df, pd.DataFrame(file_info_dict, index=[image_idx])], ignore_index=True)
                # append the bids info to the bids_info_df
                bids_info_df = pd.concat([bids_info_df, pd.DataFrame(bids_info_dict, index=[image_idx])], ignore_index=True)
                # append the label info to the labels_info_df 
                labels_info_df = pd.concat([labels_info_df, pd.DataFrame(label_info_dict, index=[image_idx])], ignore_index=True)
            else:
                logging.warning(f"File type {nifti_file_type} is not defined in the mappings. Skipping file {nifti_file_name}, {nifti_file_path}")

# Main program
if __name__ == "__main__":
    """
    Main workflow to convert NIFTI files to BIDS format

    1. Read the export_info.json file to get the subject information
    2. Create the BIDS root and derivatives dir and Patients dir (if not exists)
    3. Copy the templates: README, dataset_description, participants.json
    4. Fill the description.json
    5. Fill the participants.tsv
    6. Iterate over all Patients
        7. Create the BIDS directories for each patient
        8. Create the BIDS image files
        9. Create the BIDS sidecar files
        10. Create the BIDS labels files
        11. Create the BIDS labels sidecar files
    """
    NIFTI2BIDS()