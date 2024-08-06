# File2BIDS

The File2BIDS app is a tool that allows users to save files with a naming convention and folder structure that follows the Brain Imaging Data Structure (BIDS) standard. The app consists of two tools that can be used in sequence or individually:

1. `convert_to_BIDS.py`: This tool allows users to move or copy files to a selected BIDS project folder while renaming the files according to the standard and organizing them in the correct folder structure.
2. `BIDSsidecar_file_creator.py`: This tool allows users to generate JSON sidecar files for files named according to BIDS. The metadata fields populated in the sidecar file are reported in `samplefile_sidecar.json`.

Both tools have a GUI that guides the user through the process and require some manual input from the user. The tools are designed to help users organize and manage neuroimaging data in a consistent and standardized manner. The executables of the tools can be found in the repository's [Releases](https://github.com/IM2Neuroing/Image2BIDS2SQLite/releases/tag/v1.0.0). To run the executables, download the appropriate file for your operating system and allow them to run on your system.

## Folder overview
The tools contained in this folder allow to save files with a naming convention and folder structure which follows the Brain Imaging Data Structure standard (Gorgolewski, K. J., Auer, T., Calhoun, V. D., Craddock, R. C., Das, S., Duff, E. P., et al. (2016). The brain imaging data structure, a format for organizing and describing outputs of neuroimaging experiments. Sci. Data 3, 160044. doi: 10.1038/sdata.2016.44). This operation can be split into 2 steps, performed through 2 separate tools which can be used in sequence or individually:
1) convert_to_BIDS.py allows to move or copy files to a selected BIDS project folder while renaming the files according to the standard and organizing them in the correct folder structure
2) BIDSsidecar_file_creator.py allows to generate json sidecar files for files named according to BIDS. The metadata fields populated in the sidecar file are reported in sample_sidecar_file.json. The sidecar creation application can be activated either after converting some files to BIDS with convert_to_BIDS.py (in this case such files are already given as input to BIDSsidecar_file_creator.py) or as standalone application.
Since both steps require some manual input from the user, both application have a GUI guiding the user through the process.

## Requirements
- Python 3.x
    - PyQt6==6.7.0

## convert_to_BIDS.py
Script for a GUI allowing to organize one or more selected files in a BIDS-complieant folder structure. The main steps are:
1) BIDS project folder selection - the selected folder will be printed on the GUI
2) Selection of desired files - the selected files paths will be printed on the GUI
3) Manually fill in metadata fields required by the BIDS standard to generate the file name and folder organization. The "subject type" and "reference space" fields need to be completed only if the file is a derivative. 
    - New file types or suffixes can be provided by selecting "Other" in the dropdown list and typing the new value in the provided text field
    - The application supports batch conversion of multiple files with different subject acronyms, sessions, acquisitions, file names and reference spaces (if applicable). When multiple files are selected these fields can either be filled with:
        - One value which will be applied to all the files (e.g. one subject acronym if all the files belong to the same subject)
        - k values (where k is the number of files) separated by commas and without spaces (e.g. for 3 files from 2 subjects: sub01,sub01,sub02). The order of the values should be the same as the files order as reported on the GUI
**For labels**: the file name should be: hemisphere(L or R)-structure
4) Click on Convert files and the new BIDS-compliant file names will be printed on the GUI
5) Move or copy the files by clicking on the respective buttons. If a file with the same name is already found in the destination folder the user is
asked whether the file should be overwritten
6) (if applicable) Pass to json generator application to generate BIDS-compliant sidecar files. The moved/copied file paths will already be
passed as input to the application. The current application will be closed

## BIDSsidecar_file_creator.py
Script for a GUI allowing to generate BIDS-compliant json sidecar files for one or more selected files. 
Part of the information to be added to the sidecar file is automatically extracted from the file name and path and part has to be manually inserted by the user thorugh the GUI. Batch generation of multiple json files is possible for files having the same values in the fields which need to be manually populated by the user.
**The input files need to be already named and organized according to BIDS**

The structure of the json files is shown in the sample_sidecar_file.json.

The application can also be started after closing the BIDS converter. In this case the paths of the files moved into the BIDS folder are already passed as input. Additional files can be added with the "Add files" button.
