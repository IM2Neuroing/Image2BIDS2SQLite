import os
import datetime
import json
import logging

def add_timestamp_to_filename(filename):
    """
    Adds a timestamp for versioning to the filename.

    Args:
    filename (str): The filename to be versioned.

    Returns:
    str: The versioned filename.
    """
    # Get current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # Split filename into name and extension
    file_name, file_extension = os.path.splitext(filename)
    # Create new filename
    new_filename = f"{file_name}_{timestamp}{file_extension}"
    return new_filename


def read_config_file(file_path):
    """
    This function checks if the configuration file exists and loads it.

    Args:
    file_path (str): The path to the configuration file.

    Returns:
    dict: The configuration data.
    """
    try:
        with open(file_path, 'r') as file:
            config_data = json.load(file)
        logging.debug("Configuration file loaded")
    except FileNotFoundError:
        logging.error("Configuration file not found")
        raise
    return config_data


def copy_folder_contents(source_folder, destination_folder):
    try:
        # Ensure the source folder exists
        if not os.path.exists(source_folder):
            logging.error(f"Source folder '{source_folder}' does not exist.")
            return

        # Ensure the destination folder exists, or create it
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Iterate over all items in the source folder
        for item in os.listdir(source_folder):
            source_item = os.path.join(source_folder, item)
            destination_item = os.path.join(destination_folder, item)

            # If it's a directory, recursively copy it
            if os.path.isdir(source_item):
                copy_folder_contents(source_item, destination_item)
            else:
                # If it's a file, copy it to the destination
                shutil.copy2(source_item, destination_item)

        logging.info(f"Contents of '{source_folder}' copied to '{destination_folder}' successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")