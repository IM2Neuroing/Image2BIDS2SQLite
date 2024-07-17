import sys
import os

# Get the current script directory
current_script_directory = os.path.dirname(os.path.realpath(__file__))

# Get the root directory of your repository
root_directory = os.path.abspath(os.path.join(current_script_directory, os.pardir, os.pardir))

# Add the root directory to sys.path
sys.path.append(root_directory)

from PyUtilities import read_config_file, mkdir_if_not_exists, generate_insert_statement
import pandas as pd
import concurrent.futures
import logging
import json

# Configure logger + read config file
workflow_logger = logging.getLogger('workflow_logger')
CONFIG_FILE_PATH = 'config.json'
CONFIG = read_config_file(CONFIG_FILE_PATH)

def transform_sidecar_data(data: json) -> None:
    """
    Function to transform data of json format to sql queries for a SQLite database.
    
    Args:
    data (json): Data to be transformed.

    Returns: None
    Stores: insertSideCarData.sql

    """
    ## CHECKS
    # Check if config file is read successfully
    if CONFIG is None:
        workflow_logger.error("Config file not found or not read successfully.")
        exit()
    # Check if transformation should be skipped
    if CONFIG['skip_transformation']:
        workflow_logger.info("Transformation is skipped as per config file.")
        exit()
    # Check if data is empty
    if data is None or len(data) == 0:
        workflow_logger.error("Data is empty, no data will be transformed")
        exit()
    # Check if mapping data path exists
    if not os.path.exists(CONFIG['mapping_dir_path']):
        workflow_logger.error(f"Mapping data path does not exist: {CONFIG['mapping_dir_path']}")
        exit()
    # Check if extraction path exists
    if not os.path.exists(CONFIG['extraction_path']):
        workflow_logger.error(f"Extraction path does not exist: {CONFIG['extraction_path']}")
        exit()

    workflow_logger.info(f"Data to be transformed:\n{list(data['sidecardata'])[0:5]}")

    # define number of threads
    num_threads = 1

    # Transform data
    with concurrent.futures.ThreadPoolExecutor(num_threads) as executor:
        futures = [executor.submit(transform_sidecar_element, element) for element in data["sidecardata"].items()]

    # Get transformed data
    transformed_data = [future.result() for future in futures]
    # split the list of lists into a single list
    transformed_data = [item for sublist in transformed_data for item in sublist]
    transformed_data = pd.DataFrame(transformed_data, columns=['sql_query'])
    workflow_logger.debug(f"Transformed data:\n{transformed_data}")

    # Store transformed data
    store_transformed_data(transformed_data)

    workflow_logger.debug(f"Data transformed successfully, path: {CONFIG['datasystem_root']}/SQLiteSetup/data/transformed_data.json")
    workflow_logger.info(f"Data transformed:\n{transformed_data}")


def transform_sidecar_element(sc_element: json) -> list[str]:
    """
    Function to transform a element of image data to a one or more sql queries for a SQLite database.

    Args:
    sc_element (json): image data to be transformed.
    
    Returns: str
    Transformed data in sql format.

    """
    # init sql_queries
    sql_queries = []

    # get the file name and file information
    file, fileinformation = sc_element
    workflow_logger.debug(f"Transforming data for file: {file}")

    # assert that the file information is not empty and is a dictionary
    if fileinformation is None or not isinstance(fileinformation, dict):
        workflow_logger.error(f"File information is empty or not a dictionary for file: {file}")
        return sql_queries

    # iterate over the file information and generate sql queries
    for key, value in fileinformation.items():
        # generate sql query
        sql_query = generate_insert_statement(key, value)
        # clean sql query "" to NULL
        sql_query = sql_query.replace("''", 'NULL')
        # append to the list of sql queries
        sql_queries.append(sql_query)

    return sql_queries
    
def store_transformed_data(data: pd.DataFrame) -> None:
    """
    Function to store transformed data to a sql file.
    
    Args:
    data (pandas DataFrame): Transformed data to be stored.

    Returns: None
    Stores: insertSideCarData.sql

    """
    # mkdir "data" if not exists
    data_dir = os.path.join(CONFIG['extraction_path'])
    mkdir_if_not_exists(data_dir)

    # Save transformed data to a sql file
    data_file = os.path.join(data_dir, 'insertSideCarData.sql')
    with open(data_file, 'w') as file:
        for index, row in data.iterrows():
            file.write(row['sql_query'])
            file.write('\n')

    workflow_logger.debug(f"Transformed data stored successfully, path: {data_file}")

if __name__ == '__main__':
    # Set up logger
    workflow_logger = logging.getLogger('workflow_logger')
    workflow_logger.setLevel(logging.DEBUG)
    workflow_logger.propagate = False
    file_handler1 = logging.FileHandler('transform.log')
    formatter = logging.Formatter('%(asctime)-20s - %(levelname)-10s - %(filename)-25s - %(funcName)-25s %(message)-50s')
    file_handler1.setFormatter(formatter)
    workflow_logger.addHandler(file_handler1)

    # Extract data
    data_dir = os.path.join(CONFIG['extraction_path'])
    # Define the path to load the extracted data
    data_file = os.path.join(data_dir, 'extracted_data.json')
    if not os.path.exists(data_file):
        workflow_logger.error(f"Extracted data file does not exist: {data_file}")
        exit()
    data = json.load(open(data_file))
    transform_sidecar_data(data)