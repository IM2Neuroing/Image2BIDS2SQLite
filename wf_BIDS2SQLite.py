from ETL.Extract.extract import extract_sidecar_data
from ETL.Transform.transform import transform_sidecar_data
from ETL.Load.load import load_sidecar_data
from ETL.PostTransform.post_transformation import clean_image_tables,backpropation

import logging

# Main Workflow function
def workflow_BIDS2SQLite():
    """
    This function is the workflow of the ETL process.
    It calls the extract_sidecar_data, transform_sidecar_data, and load_data functions.
    """
    # Log the start of the workflow
    workflow_logger.info("Workflow started.")
    # Extract data
    extracted_data = extract_sidecar_data()
    workflow_logger.info("Data extracted successfully.")

    # Transform data
    transform_sidecar_data(extracted_data)
    workflow_logger.info("Data transformed successfully.")

    # Load data
    load_sidecar_data()
    workflow_logger.info("Workflow finished successfully.")

    # Post Transformation
    clean_image_tables()
    
    # Backpropagation to BIDS
    backpropation()


# Main program
if __name__ == "__main__":
    """
    This is the main program that will be executed when the script is run.
    It calls the main_workflow function to execute the ETL process.
    1) Extract data from BIDS sidecar files
    2) Transform the data, according to the mapping rules.
    3) Load the transformed data into the destination database. SQLite in this case.
    """
    # Configure logger
    workflow_logger = logging.getLogger('workflow_logger')
    workflow_logger.setLevel(logging.INFO)
    file_handler1 = logging.FileHandler('Workflow-debug.log')
    formatter = logging.Formatter('%(asctime)-20s - %(levelname)-10s - %(filename)-25s - %(funcName)-25s %(message)-50s')
    file_handler1.setFormatter(formatter)
    workflow_logger.addHandler(file_handler1)

    # Execute the main workflow
    workflow_BIDS2SQLite()