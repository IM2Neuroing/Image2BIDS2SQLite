import os
import shutil
from os.path import join, splitext
from pathlib import Path
import hashlib

def calculate_hash(filename, hash_type="sha256"):
  """
  Calculates the hash of a file.

  Args:
    filename: The path to the file.
    hash_type: The type of hash algorithm to use (e.g., "md5", "sha256", "sha1").

  Returns:
    The hash of the file as a hexadecimal string.
  """
  
  # Open the file in binary mode
  with open(filename, "rb") as f:
    # Create a hash object
    hasher = hashlib.new(hash_type)
    
    # Read the file in chunks and update the hash
    chunk_size = 4096  # You can adjust this value based on your needs
    while True:
      chunk = f.read(chunk_size)
      if not chunk:
        break
      hasher.update(chunk)
    
    # Return the hash as a hexadecimal string
    return hasher.hexdigest()
    

def mkdir_if_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)


def copy_dir_structure(in_path, out_path, root_dirs_to_ignore, keep_json=False, ignore_files=True):
    """
    using the 'ignore_files' function the directory structure is copied without copying
        the files if ignore files is set to true
    :param keep_json:
    :param root_dirs_to_ignore:
    :param ignore_files:
    :param in_path:
    :param out_path:
    :return:
    """

    is_out_dir_subdir = check_if_subdir(in_path, out_path)
    print(f'is_out_dir_subdir: {is_out_dir_subdir}')

    if ignore_files is True:
        if keep_json is True:
            shutil.copytree(in_path, out_path, ignore=ignore_files_except_json_fct)
        else:
            shutil.copytree(in_path, out_path, ignore=ignore_all_files_fct)
    else:
        shutil.copytree(in_path, out_path)

    if len(root_dirs_to_ignore) > 0:
        for root_dir_to_ignore in root_dirs_to_ignore:
            shutil.rmtree(join(out_path, root_dir_to_ignore))


def ignore_all_files_fct(directory, files):
    """
    defining the function to ignore all the files if present in any folder
    :param directory:
    :param files:
    :return:
    """
    return [f for f in files if os.path.isfile(os.path.join(directory, f))]


def ignore_files_except_json_fct(directory, files):
    """
    defining the function to ignore the files if present in any folder, except for json files
    :param directory:
    :param files:
    :return:
    """
    return [f for f in files if os.path.isfile(os.path.join(directory, f)) and
            '.json' not in splitext(f)[1]]


def check_if_subdir(top_dir, child_dir):
    top_dir = Path(top_dir)
    child_dir = Path(child_dir)
    is_subdir = top_dir in child_dir.parents
    # print(top_dir in child_dir.parents)

    return is_subdir
