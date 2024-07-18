import sys
import os

# Add the parent directory to the sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# Now you can import the function from the script
from PyUtilities.setupFunctions import read_config_file

import pandas as pd
import os

# open export_info.json using pandas
def open_export_info_json(export_info_json):
    with open(export_info_json) as f:
        assert f.readable()
        # assert that the file is not empty
        assert os.path.getsize(export_info_json) > 0
        assert f.name.endswith('.json')
        export_info = pd.read_json(f)
    return export_info

# iterate through all directories in 4bidsfolder and add them to export_info.json if they are not already there;
 # {  "record_id": 50 + 7 from CF07,
 #   "patient_id": "11_s_p_36_m_CF01",
 #   "exported": true,
 #   "exporter": "unknown",
 #   "exportdate": "unknown",
 #   "comment": null,
 #   "folder_name": "11_s_p_36_m_CF01"
 # }
def add_directories_to_export_info(export_info, bids_folder):
    if not isinstance(export_info, pd.DataFrame):
        raise ValueError("export_info should be a pandas DataFrame")
    for root, dirs, files in os.walk(bids_folder):
        for d in dirs:
            if d not in export_info.folder_name.values:
                record_id = 50 + int(d.split('_')[5][2:4])
                patient_id = d
                new_row = pd.DataFrame({'record_id': [record_id], 'patient_id': [patient_id], 'exported': [False], 'exporter': ['unknown'], 'exportdate': ['unknown'], 'comment': [None], 'folder_name': [d]})
                export_info = export_info._append(new_row, ignore_index=True)
    return export_info

# write export_info.json
def write_export_info_json(export_info, export_info_json):
    export_info.to_json(export_info_json, orient='records')

# main
def main():
    # get config data
    config_data = read_config_file('config.json')
    # prepare paths
    dir_4bids_path = os.path.join(config_data["datasystem_root"], config_data["4bids_dir_name"])
    file_export_info_path = os.path.join(dir_4bids_path,"export_info.json")

    # open export_info.json
    export_info = open_export_info_json(file_export_info_path)
    export_info = add_directories_to_export_info(export_info, dir_4bids_path)
    write_export_info_json(export_info, file_export_info_path)

if __name__ == '__main__':
    main()
