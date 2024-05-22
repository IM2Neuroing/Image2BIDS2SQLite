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

# Configure logger + read config file
workflow_logger = logging.getLogger('workflow_logger')
CONFIG_FILE_PATH = 'config.json'
CONFIG = read_config_file(CONFIG_FILE_PATH)

def transform_sidecar_data(data: pd.DataFrame) -> None:
    """
    Function to transform data of pandas DataFrame format to sql queries for a SQLite database.
    
    Args:
    data (pandas DataFrame): Data to be transformed.

    Returns: None
    Stores: insertSideCarData.sql

    """
    # Check if data is empty
    if data.empty:
        workflow_logger.error("Data is empty, no data will be transformed")
        exit()

    # Check if mapping data is empty or does not exist
    if (CONFIG['mapping_dir_path'] is None) or (not os.path.exists(CONFIG['mapping_dir_path'])):
        workflow_logger.error("Mapping data is empty or does not exist, no data will be transformed")
        exit()

    workflow_logger.info(f"Data to be transformed:\n{data}")

    # Get mapping data
    mapping_files_table = pd.read_csv(os.path.join(CONFIG['mapping_dir_path'], '1-0-files.csv'))
    mapping_bids_table = pd.read_csv(os.path.join(CONFIG['mapping_dir_path'], '2-0-bids.csv'))
    mapping_labels_table = pd.read_csv(os.path.join(CONFIG['mapping_dir_path'], '3-0-labels.csv'))
    workflow_logger.info(f"Mapping data:\n{mapping_files_table}\n{mapping_bids_table}\n{mapping_labels_table}")

    # define number of threads
    num_threads = 1

    # Transform data
    with concurrent.futures.ThreadPoolExecutor(num_threads) as executor:
        futures = [executor.submit(transform_image_row, row, mapping_files_table, mapping_bids_table, mapping_labels_table) for row in data.iterrows()]

    # Get transformed data
    transformed_data = [future.result() for future in futures]
    # split the list of lists into a single list
    transformed_data = [item for sublist in transformed_data for item in sublist]
    transformed_data = pd.DataFrame(transformed_data, columns=['sql_query'])
    workflow_logger.debug(f"Transformed data:\n{transformed_data}")

    # Store transformed data
    store_transformed_data(transformed_data)

    workflow_logger.debug(f"Data transformed successfully, path: {CONFIG['datasystem_root']}/SQLiteSetup/data/transformed_data.csv")
    workflow_logger.info(f"Data transformed:\n{transformed_data}")


def transform_image_row(row: pd.Series, mapping_files_table: pd.DataFrame, mapping_bids_table: pd.DataFrame, mapping_labels_table: pd.DataFrame) -> list[str]:
    """
    Function to transform a row of image data to a one or more sql queries for a SQLite database.

    Args:
    row (pandas Series): Row of image data to be transformed.
    mapping_files_table (pandas DataFrame): Mapping data for files table.
    mapping_bids_table (pandas DataFrame): Mapping data for BIDS table.
    mapping_labels_table (pandas DataFrame): Mapping data for labels table.

    Returns: str
    Transformed data in sql format.

    """
    # Get file data
    file_data = map_data(mapping_files_table, row)

    # Get BIDS data
    bids_data = map_data(mapping_bids_table, row)

    # Get labels data
    labels_data = map_data(mapping_labels_table, row)

    # Create sql query
    sql_queries = []

    # append sql query for files table
    sql_query = generate_insert_statement("files", file_data)
    sql_queries.append(sql_query)

    # append sql query for BIDS table
    sql_query = generate_insert_statement("bids", bids_data)
    sql_queries.append(sql_query)

    # append sql query for labels table
    sql_query = generate_insert_statement("labels", labels_data)
    sql_queries.append(sql_query)

    return sql_queries

def map_data(mapping_table: pd.DataFrame, row: pd.Series) -> dict:
    """
    Function to map data to the corresponding columns in the mapping table.

    Args:
    mapping_table (pandas DataFrame): Mapping data for a table.
    row (pandas Series): Row of data to be mapped.

    Returns: dict
    Mapped data.

    """
    data = {}
    for index, mapping_row in mapping_table.iterrows():
        workflow_logger.debug(f"Mapping row: {mapping_row}")
        workflow_logger.debug(f"Row: {row}")
        workflow_logger.debug(f"Attribute: {mapping_row['Attribute']}")
        workflow_logger.debug(f"Field name: {mapping_row['field_name']}")
        data[mapping_row['Attribute']] = getattr(row, mapping_row['field_name'])
    return data

def getattr(row: tuple, field_name: str)-> str:
    """
    Function to get the value of a field in a row.

    Args:
    row (tuple): Row of data.
    field_name (str): Field name.

    Returns: str
    Value of the field.
    """
    # check if field_name is None or not a string
    if field_name is None or not isinstance(field_name, str):
        workflow_logger.error(f"Field name is None or not a string: {field_name}")
        return None
    elif field_name[:4] == "AUTO":
        return None
    elif field_name[:4] == "DROP":
        return field_name
    elif field_name[:4] == "FUNC":
        function_string = field_name[5:-1]
        try:
            variable = function_string.split(";")[0]
            function_string = function_string.split(";")[1]
            workflow_logger.debug(f"Variable: {variable}")
            workflow_logger.debug(f"Function: {function_string}")
            value = row[1][variable]
            workflow_logger.debug(f"Value: {value}")
            function_string = function_string.replace('xVARIABLEx', value)
            workflow_logger.debug(f"Function: {function_string}")
            # Execute the function in a safe environment
            result = eval(function_string)
            workflow_logger.debug(f"result: {result}")
            return result
        except:
            workflow_logger.error(f"Function did not work : {function_string}")
            return None
    else:
        try:
            value = row[1][field_name]
            wp = workflow_logger.debug(f"Value: {value}")
            return value
        except:
            workflow_logger.error(f"Field name does not exist in the row: {field_name}")
            return "NULL"
    
def store_transformed_data(data: pd.DataFrame) -> None:
    """
    Function to store transformed data to a sql file.
    
    Args:
    data (pandas DataFrame): Transformed data to be stored.

    Returns: None
    Stores: insertSideCarData.sql

    """
    # mkdir "data" if not exists
    data_dir = os.path.join(CONFIG['datasystem_root'],'SQLiteSetup/data')
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
    data = pd.read_csv(os.path.join(CONFIG['datasystem_root'],'SQLiteSetup/data/extracted_data.csv'))
    transform_sidecar_data(data)