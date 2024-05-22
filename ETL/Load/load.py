import sys
import os

# Get the current script directory
current_script_directory = os.path.dirname(os.path.realpath(__file__))

# Get the root directory of your repository
root_directory = os.path.abspath(os.path.join(current_script_directory, os.pardir, os.pardir))

# Add the root directory to sys.path
sys.path.append(root_directory)

from PyUtilities.setupFunctions import read_config_file
from PyUtilities.databaseFunctions import create_database, execute_sql_script, data_check
import logging

CONFIG_FILE_PATH = 'config.json'
CONFIG = read_config_file(CONFIG_FILE_PATH)
# Configure logger
workflow_logger = logging.getLogger('workflow_logger')

def load_sidecar_data():
    """
    Function to load data into the destination database.
    """
    ## DATA LOADING
    workflow_logger.info("Data loading started.")
    load_siglefile_data_into_database()
    workflow_logger.info("Data loaded into the database.")

    ## CHECK IF DATA LOADED
    data_check(CONFIG['db_path'])

# Load data into database Function
def load_siglefile_data_into_database():
    """
    Function to load the data into the destination database.
    Check if the sqlite database is created.
    Check if sql files are provided, in the data folder.
    Execute the sql files to load the data into the database.
    """

    # Check if the data should be loaded into the database
    if CONFIG['db_load_data'] is True:
      # Check if data_path CONFIG from file is valid
      if CONFIG['data_path'] is None:
        workflow_logger.error("No data path was specified in the config file")
        exit()
      # Check if the database path is valid
      if CONFIG['db_path'] is None:
        workflow_logger.error("No database path was specified in the config file")
        exit()
      # check for single sqlfile in the data folder: data/insertSideCarData.sql
      if os.path.isfile(f"{CONFIG['data_path']}"):
        sql_file = f"{CONFIG['data_path']}"
        # Execute the SQL file
        with open(sql_file, 'r') as file:
          sql = file.read()
          # Execute the SQL
          execute_sql_script(sql,CONFIG['db_path'])

      workflow_logger.debug("Data loaded into SQLite Database")

if __name__ == "__main__":
    # Set up logger
    workflow_logger = logging.getLogger('workflow_logger')
    workflow_logger.setLevel(logging.DEBUG)
    workflow_logger.propagate = False
    file_handler1 = logging.FileHandler('load.log')
    formatter = logging.Formatter('%(asctime)-20s - %(levelname)-10s - %(filename)-25s - %(funcName)-25s %(message)-50s')
    file_handler1.setFormatter(formatter)
    workflow_logger.addHandler(file_handler1)

    # Load data
    load_sidecar_data()