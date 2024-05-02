from ETL.Transform.tf_NIFTI2BIDS import NIFTI2BIDS

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
    
