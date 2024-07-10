import json
import os
import hashlib

# Dictionary mapping the file extension to the datatype
data_dict = {
    "nii.gz": "NifTI",
    "txt": "Text",
    "vtp": "VTK surface model",
    "mat": "MATLAB file",
    "h5": "Hierarchical Data Format",
    "mph": "Multiphysics simulation file",
    "seg.nrrd": "Segmentation labelmap",
    "stl": "CAD file",
    "png": "Portable Network Graphic",
    "json": "JavaScript Object Notation"
}




def extract_info_from_filename(file, is_label=False, is_transformed = False):
    """
    The function extracts information about the file contained in the file name which follows the BIDS naming standard. If some information is not found,
    the corresponding parameter is set to NA.

    Args:
        file: string containing the file absolute path 
        is_label: bool value indicating whether the file is a label
        is_transformed: bool value indicating whether the file is a transformed

    Returns:
        info_dict: dictionary with the following information:
            -subject: string with subject alphanumeric identification code (e.g. <subject>)
            -session: string with information about the session in which the file was acquired (e.g. <Pre|Post>)
            -acquisition: string with information about the image acquisition (e.g. <ppp>)
            -suffix: last word before file extension, gives information on the type of file we have (e.g. warp)
            -extension: file extension (e.g. nii.gz)
            -hemisphere (applicable only to labels): R or L 
            -structure (applicable only to labels): name of structure that the label identifies
            -file_id: file hash
            -relative_sidecar_path: name of sidecar json file
            -file_type: e.g. Segmentation, Transform...
            -bids_datatype: type of file - can be obtained from the extension
        The other fields expected by the json file structure are generated but left empty for the moment
    """
    info_dict = {}

    # Get only file name
    file_name = file.split('/')[-1]

    # Create file hash
    file_hash = calculate_hash(file)

    # Get file type
    file_type = file.split('/')[-2]

    # Extract other information
    bids_info = file_name.split('_')
    subject = session = acquisition = suffix = extension = hemisphere = structure = 'NA'
    # Loop through bids_info elements except the last one (which we know it contains the suffix+file extension)
    for i in range(len(bids_info)-1):
        if 'sub' in bids_info[i]:
            subject = bids_info[i].split('-')[1]
        elif 'ses' in bids_info[i]:
            session = bids_info[i].split('-')[1]
        elif 'acq' in bids_info[i]:
            acquisition = bids_info[i].split('-')[1]
    # Get file suffix and extension
    suffix = bids_info[-1].split('.', 1)[0]
    extension = bids_info[-1].split('.', 1)[1]
    # If file is a label get hemisphere and structure from file name
    if is_label:
        hemisphere = bids_info[-2].split('-', 1)[0]
        structure = bids_info[-2].split('-', 1)[1]
    else:
        pass

    # Create sidecar file name
    sidecar_file = f"{file_name.split('.', 1)[0]}_sidecar.json"

    # Check if the extension is present in the datatype dictionary
    if extension in list(data_dict.keys()):
        datatype = data_dict[extension]
    else:
        datatype = "Unknown"

    info_dict = {"files": {"file_id": file_hash, "subject_id": "", "electrode_id": "", "file_path": file,
        "file_type": file_type, "source_id": "", "transformation_id": ""}, "bids": {"file_id": file_hash,
        "modality": "", "protocol_name": "", "stereotactic": "", "dicom_image_type": "","acquisition_date_time": "", 
        "relative_sidecar_path": sidecar_file,"bids_subject": subject,"bids_session": session,"bids_extension": extension,
        "bids_datatype": datatype,"bids_acquisition": acquisition,"bids_suffix": suffix}
    }

    # If it is a label add the label related fields to dictionary - some of them will be filled later through GUI
    if is_label:
       label_dict = {"is_label": "yes", "file_id": file_hash, "hemisphere": hemisphere, \
                     "structure": structure, "color": "", "comment": ""}
       info_dict["labels"] = label_dict
       
    # If the file has been transformed add related fields to dictionary - some of them will be filled later through GUI
    if is_transformed:
       transformation_dict = {"is_transformation": "yes", "transformation_id":"", "identity":"", \
                              "target_id": "", "transform_id": ""}
       info_dict["transformations"] = transformation_dict
    
    return info_dict

def calculate_hash(filename, hash_type="sha256"):
  """
  Calculates the hash of a file.
 
  Args:
    filename: The path to the file.
    hash_type: The type of hash algorithm to use (e.g., "md5", "sha256", "sha1").
 
  Returns:
    The hash of the file as a hexadecimal string.
  """
  
  # Open the file in binary mode
  with open(filename, "rb") as f:
    # Create a hash object
    hasher = hashlib.new(hash_type)
    
    # Read the file in chunks and update the hash
    chunk_size = 4096  # You can adjust this value based on your needs
    while True:
      chunk = f.read(chunk_size)
      if not chunk:
        break
      hasher.update(chunk)
    
    # Return the hash as a hexadecimal string
    return hasher.hexdigest()