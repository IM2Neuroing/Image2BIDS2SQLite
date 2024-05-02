import os
import pandas as pd
import json
from tkinter import filedialog, ttk
from tkinter import *
import logging


def read_tsv_from_df(fname):
    df = pd.read_csv(fname, delimiter='\t')
    return df


def write_tsv_from_df(fname, df):
    df.to_csv(fname, sep='\t', index=False)


def read_json_to_dict(fname):
    with open(fname, 'r') as file:
        data = json.load(file)
    return data


def write_json_from_dict(fname, data_dict):
    with open(fname, 'w') as file:
        json.dump(data_dict, file, indent=4)


def listdir_no_hidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f


def select_dir_from_tk():
    """
    :return:
    """
    path = filedialog.askdirectory()
    return path


def tk_warning_message(message, button_text, font='Aerial 18 bold'):
    win = Tk()
    win.geometry("750x250")
    Label(win, text=message, font=font).pack(pady=20)
    button = ttk.Button(win, text=button_text, command=win.destroy)
    button.pack(ipadx=5, pady=15)
    win.mainloop()

def csvs_reader(folder_path):
    # Get a list of all CSV files in the folder
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
    # Sort the CSV files by filename
    csv_files = sorted(csv_files)
    logging.debug("Found mapping CSVs %s", str(csv_files))
    
    # Iterate through each CSV file
    for csv_file in csv_files:
        # Construct the full path to the CSV file
        csv_path = os.path.join(folder_path, csv_file)
        
        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(csv_path)
        logging.debug("Read in: %s", str(csv_path))
        
        # Yield the DataFrame to the caller
        yield df