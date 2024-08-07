# Image to BIDS to SQLite ETL Tool

## Introduction

This repository is a collection of workflows, pipelines and python-tools to extract data from IMAGES to transform them into BIDS format and load them into a SQLite database. The tool is designed to be flexible and can be adapted to different data sources and target data models.

## The different Pipelines & Workflows

- *Fil2BIDS* (APP with GUI)
  - GUI-supported pipeline to move/copy files in a BIDS project folder following the BIDS naming standard and generate the json sidecar files with the relevant file metadata. 
   
- *ETL* (Extract, Transform, Load) workflows:
  - NIFTI to BIDS conversion (wf_NIFTI2BIDS.py) (under development)
    -  The ETL process extracts NIFTI images from the 4bids folder, renames them according to the Brain Imaging Data Structure (BIDS) standard, and then loads the renamed files into a newly constructed BIDS-compliant directory. This ensures the data adheres to the BIDS standard for consistent and organized neuroimaging data storage.
  - Slicer BIDS integration (wf_Slicer2BIDS.py) (under development)
    - The ETL process extracts 3D Slicer scene images from the 4bids folder, renames them following the Brain Imaging Data Structure (BIDS) standard, and loads the renamed files into a newly created BIDS-compliant directory. This process ensures that the neuroimaging data is consistently organized and adheres to the BIDS specifications.
  - BIDS to SQLite (wf_BIDS2SQLite.py) (stable / dockerized)
    - The ETL process extracts metadata from the sidecar files (IMAGE_sidecar.json) in a BIDS directory and stores this information in an SQLite database located within the Image Management System directory. This ensures the metadata is organized and accessible for efficient image management and retrieval.

## Folder Structure

The repository is structured as follows:

    ```bash
    ├── README.md
    ├── LICENSE
    ├── requirements.txt
    ├── config_example.json
    ├── config_docker_example.json **** (Docker config file template)
    ├── wf_BIDS2SQLite.py  **** (BIDS to SQLite ETL workflow)
    ├── wf_NIFTI2BIDS.py    **** (NIFTI to BIDS ETL workflow)
    ├── wf_Slicer2BIDS.py   **** (Slicer to BIDS ETL workflow)
    ├── docker-compose_****.yml **** (Docker-compose file for running the ETL processes)
    ├── dockerfile_xxxx **** (Dockerfile for the ETL processes)
    ├── crontab **** (Crontab file for scheduling the ETL processes in docker)
    ├── ETL
    │   ├── Extract    **** (Extract Transform Load scripts)
    │   ├── Transform 
    │   └── Load
    ├── File2BIDS **** (App with GUI)
    │   └── ****  (save files with a naming convention and folder structure which follows the Brain Imaging Data Structure standard)
    ├── IMS **** (Demo data system location)
    │   ├── BIDS **** (Brain Imaging Data Structure directory, containing the imagedata in BIDS format)
    │   └── IMS.db **** (SQLite database, containing the imagemetadata in a relational format)
    ├── IMS_setup **** (Demo data system setup)
    │   ├── Mappingtables **** (Mapping tables for the transformation process)
    │   ├── bids_templates **** (BIDS templates for the transformation process)
    │   ├── 4BIDS **** (Directory containing the images to populate the BIDS directory)
    │   └── SQLite_setup **** (SQLite schema for the database creation process)
    └── PyUtilities **** (Python utilities)
    ```

## Running the File2BIDS App

    ```bash
    └── File2BIDS **** (App with GUI)
        ├── ****  (save files with a naming convention and folder structure which follows the Brain Imaging Data Structure standard)

    ```

Follow the instructions in the [README.md](File2BIDS/README.md) file in the File2BIDS directory to run the app.

## Running any of the ETL Processes

### System Setup and Run Instructions

#### Docker Environment Setup

1. Ensure Docker and Docker-compose are installed on your system. You can verify this by running `docker --version` and `docker-compose --version`  in your terminal.
2. Clone this repository to your local machine.
3. Navigate to the root directory of the cloned repository.
4. Define the Data Model as described in the "Data Model Definition" in section below.
5. Create a `config_docker.json` file in the root directory. You can use the `config_docker_example.json` file as a template. Define the parameters as described in the "Config File Setup" section below.
6. Run the docker-compose file by running `docker-compose -f docker-compose_****.yml up`.
7. The ETL process will start automatically, and repeat every 6 hours.
8. To stop the ETL process, run `docker-compose down`.

#### Python Environment Setup

1. Ensure Python 3.10.x is installed on your system. You can verify this by running `python --version` in your terminal.
2. Clone this repository to your local machine.
3. Navigate to the root directory of the cloned repository.
4. It is recommended to create a virtual environment to isolate the project dependencies. You can do this by running `python -m venv venv`.
5. Activate the virtual environment by running `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows).
6. Install the required Python packages by running `pip install -r requirements.txt`.
7. Define the Data Model as described in the "Data Model Definition" in section below.
8. Create a `config.json` file in the root directory. You can use the `config_example.json` file as a template. Define the parameters as described in the "Config File Setup" section below.
9. Run the ETL process by running `python wf_*****.py`.

### Config File Setup

1. Create a `config.json` file in the root directory. This file will store the configuration parameters for the ETL workflows. You can use the `config_example.json` file as a template.
2. Define the following parameters in the `config.json` file:

```json

{   
    "__MAIN__config" : "version 1.0", # version of the main config file
    "repository_root": "path/to/repo/Image2BIDS2SQLite/", # path to the root directory of the repository
    "datasystem_root": "path/to/repo/Image2BIDS2SQLite/IMS", # path to the root directory of the final data system location
    "bids_dir_path": "path/to/repo/Image2BIDS2SQLite/IMS/BIDS", # path to the BIDS directory
    "__BIDS_2_SQLite__config":"2.0", # version of the BIDS to SQLite config file
    "skip_extraction": false, # skip the extraction process
    "extraction_path" : "path/to/repo/Image2BIDS2SQLite/IMS_setup/SQLite_setup", # path to the directory, where the extraction files are stored
    "skip_transformation": false, # skip the transformation process
    "mapping_dir_path": "path/to/repo/Image2BIDS2SQLite/IMS_setup/Mappingtables", # path to the directory, where the mapping files are stored
    "skip_db_creation" : false, # skip the database creation process
    "db_schema": "path/to/repo/Image2BIDS2SQLite/IMS_setup/SQLite_setup/sqlite_schema.sql", # path to the SQLite schema file
    "skip_loading": false, # skip the loading process
    "db_path": "path/to/repo/Image2BIDS2SQLite/IMS/IMS.db", # path to the SQLite database
    "skip_image_cleaning" : false, # skip the image cleaning process
    "skip_backpropagation": false, # skip the backpropagation process
    "__NIFTI_2_BIDS__config" : "1.0", # version of the NIFTI to BIDS config file
    "4bids_dir_name": "4BIDS", # name of the directory, where the images are stored to populate the BIDS directory
    "__SLICER_2_BIDS_config" : "1.0", # version of the Slicer to BIDS config file
    "slicer_dir_name" : "slicer_scenes_clean" # name of the directory, where the Slicer scenes are stored to populate the BIDS directory
}
```

### Data Model Definition

Define the data model for the target database. This will include the tables and columns that will be created in the SQLite database. The data model should be defined in a SQL schema file. You can use the `SQLite_setup/sqlite_schema.sql` file as a template or as a starting point.

## License

This project is licensed under the MIT License. This means you are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, under the conditions that you include the following:

1. A copy of the original MIT License in any redistributed copies or substantial portions of the software.
2. A clear acknowledgement of the original source of the software.

For more details, please see the [LICENSE](LICENSE) file in the project root.

## Contributing

Contributions, issues, and feature requests are welcome!

***Enjoy transferring data from REDCap to SQLite efficiently and reliably!***
