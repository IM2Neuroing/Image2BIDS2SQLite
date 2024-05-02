import shutil
import os
import pandas as pd
from os.path import join

from PyUtilities.read_write import read_tsv_from_df, write_tsv_from_df, read_json_to_dict, write_json_from_dict

fname_ds_desc = 'dataset_description.json'
fname_readme = 'README'
fname_participants_json = 'participants.json'


def copy_templates_to_bids_root(readme_t, ds_desc_t, part_json_t, bids_root):
    shutil.copy(readme_t, join(bids_root, fname_readme))
    shutil.copy(ds_desc_t, join(bids_root, fname_ds_desc))
    shutil.copy(part_json_t, join(bids_root, fname_participants_json))


def add_participants_ids_to_tsv(bids_root, subjects):
    """
    set up a simple participants.json
    :param bids_root:
    :param subjects:
    :return:
    """
    fname = join(bids_root, fname_participants_json)
    df = pd.read_json(fname)

    # Get common columns
    common_columns = df.columns.intersection(subjects.columns)  # Get the common column names
    # only keep the common columns
    df = subjects[common_columns]
    # Write the dataframe to a new TSV file
    write_tsv_from_df(fname.replace('.json', '.tsv'), df)
    return df

def change_dataset_name(bids_root,dataset_name = None):
    if dataset_name is None:
        dataset_name = os.path.basename(bids_root)
    ds_desc_dict = read_json_to_dict(join(bids_root, fname_ds_desc))
    ds_desc_dict['Name'] = dataset_name
    write_json_from_dict(join(bids_root, fname_ds_desc), ds_desc_dict)
    return ds_desc_dict
