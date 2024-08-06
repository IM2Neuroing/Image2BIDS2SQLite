"""
Script for a GUI allowing to organize one or more selected files in a BIDS-complieant folder structure. The main steps are:
1) BIDS project folder selection - the selected folder will be printed on the GUI
2) Selection of desired files - the selected files paths will be printed on the GUI
3) Manually fill in metadata fields required by the BIDS standard to generate the file name and folder organization. The "subject type"
and "reference space" fields need to be completed only if the file is a derivative. 
    - New file types or suffixes can be provided by selecting "Other" in the dropdown list and typing the new value in the provided text field
    - The application supports batch conversion of multiple files with different subject acronyms, sessions, acquisitions, file names 
        and reference spaces (if applicable). When multiple files are selected these fields can either be filled with:
            - One value which will be applied to all the files (e.g. one subject acronym if all the files belong to the same subject)
            - k values (where k is the number of files) separated by commas and without spaces (e.g. for 3 files from 2 subjects: sub01,sub01,sub02)
*** For labels: the file name should be: hemisphere(L or R)-structure
4) Click on Convert files and the new BIDS-compliant file names will be printed on the GUI
5) Move or copy the files by clicking on the respective buttons. If a file with the same name is already found in the destination folder the user is
asked whether the file should be overwritten
6) (if applicable) Pass to json generator application to generate BIDS-compliant sidecar files. The moved/copied file paths will already be
passed as input to the application. The current application will be closed
"""

import sys
import json
import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, 
    QLineEdit, QCheckBox, QLabel, QMessageBox, QFrame, QScrollArea, QComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import gui_functions as gf
import subprocess


original_files_list:list
original_files_list = [] # List with selected files to be moved to BIDS
bids_files_list:list
bids_files_list = [] # List with files names converted to BIDS
bids_folder = "" # String with path to BIDS folder

class BIDSConverter(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("File to BIDS converter")

        # Set initial window size
        self.setGeometry(100, 100, 400, 300)

        # Define layout
        layout_h0 = QHBoxLayout() # For explanation label and layout_v0
        layout_h1 = QHBoxLayout() # For "Add" and "Clear" button
        layout_h2 = QHBoxLayout() # For generate names button and proposed names label
        layout_h3 = QHBoxLayout() # For move, copy, generate json button
        layout_h4 = QHBoxLayout() # For layout_v1, layout_v2, layout_v3

        layout_v0 = QVBoxLayout() # For BIDS folder path selection button and label
        layout_v1 = QVBoxLayout() # For layout_h1 and selected files scroll bar
        layout_v1.setContentsMargins(10, 10, 10, 10)
        layout_v2 = QVBoxLayout() # For derivative checkbox, subject type list, file type list, other text field, space text field
        layout_v2.setContentsMargins(10, 10, 10, 10)
        layout_v3 = QVBoxLayout() # For subject acr text field, session text field, acquisition text field, suffix text field, file name text field
        layout_v3.setContentsMargins(10, 10, 10, 10)
        layout_v4 = QVBoxLayout() # For layout_h0, layout_h4, layout_h2, layout_h3

        # Label explaining how to use the GUI
        self.explanation_label = QLabel(self)
        self.explanation_label.setText('This application allows to organize files in a BIDS compliant folder structure <br>'
                                       '1) Select BIDS project folder <br>'
                                       '2) Add the files which need to be saved in a BIDS compliant manner <br>'
                                       '3) Fill in the required fields. Multiple files with different subject acronyms, sessions, acquisitions, file names and\n\
                                        reference spaces can be processed at once. In this case multiple values (<b>comma separated and without spaces</b>) can be typed in the text fields.<br>'
                                        '<b>Important</b>: the values should be provided in the same order as the selected files. <b>For labels</b>: file name should be of the type hemisphere(R/L)-structure<br>'
                                        '4) Click on Convert files and the new BIDS-compliant file names will be shown<br>'
                                        '5) Move or copy files in destination<br>'
                                        '6) Pass to sidecar generator application (the copied/moved files will already be provided as input)')
        self.explanation_label.setWordWrap(True)  # Enable text wrapping
        self.explanation_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_h0.addWidget(self.explanation_label)

        # BIDS project folder selection button
        self.bids_folder_button = QPushButton('Browse', self)
        self.bids_folder_button.clicked.connect(self.select_folder)
        layout_v0.addWidget(self.bids_folder_button)

        # Label to show selected BIDS folder
        self.bids_folder_label = QLabel('Select BIDS folder ', self)
        self.bids_folder_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Scrollable area in which to embed the selected folder label
        self.bids_folder_scroll_area = QScrollArea(self)
        self.bids_folder_scroll_area.setWidgetResizable(True)
        self.bids_folder_scroll_area.setWidget(self.bids_folder_label)
        self.bids_folder_scroll_area.setFixedSize(160,100)
        layout_v0.addWidget(self.bids_folder_scroll_area)

        line0 = QFrame()
        line0.setFrameShape(QFrame.Shape.VLine)
        line0.setFrameShadow(QFrame.Shadow.Sunken)

        layout_h0.addWidget(line0)

        layout_h0.addLayout(layout_v0)

        # File selection button
        self.add_file_button = QPushButton('Add Files', self)
        self.add_file_button.clicked.connect(self.select_multiple_files)
        layout_h1.addWidget(self.add_file_button)

        # Clear button
        self.clear_button = QPushButton('Clear', self)
        self.clear_button.clicked.connect(self.clear_files)
        layout_h1.addWidget(self.clear_button)  
        
        # Label to show selected files
        self.file_label = QLabel('Selected files: ', self)
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Scrollable area in which to embed the selected files label - we expect the text to be long if many files are selected
        self.files_scroll_area = QScrollArea(self)
        self.files_scroll_area.setWidgetResizable(True)
        self.files_scroll_area.setWidget(self.file_label)
        self.files_scroll_area.setFixedSize(500,160)

        layout_v1.addLayout(layout_h1)
        layout_v1.addWidget(self.files_scroll_area)

        # Checkbox indicating whether the file is a derivative
        self.checkbox_derivative = QCheckBox("Is the file a derivative?", self)
        self.checkbox_derivative.stateChanged.connect(self.toggle_der_inputs)
        layout_v2.addWidget(self.checkbox_derivative)

        # Label for subject type
        self.subj_type_label = QLabel('Choose subject type: ', self)
        layout_v2.addWidget(self.subj_type_label)
        
        # Combo box with choices of subject type
        self.combobox_subj_type = QComboBox(self)
        subj_type_options = ['Patients', 'Atlases', 'Electrodes']
        self.combobox_subj_type.addItems(subj_type_options)
        layout_v2.addWidget(self.combobox_subj_type)

        # Label for file type
        self.file_type_label = QLabel('Choose file type: ', self)
        layout_v2.addWidget(self.file_type_label)

        # Combo box with choices of file type - if the user chooses other he can type
        self.combobox_file_type = QComboBox(self)
        file_type_options = ['anat', 'Preprocessed', 'Simulations', 'Transforms', 'PatientInAtlas',
                   'AtlasInPatient', 'Segmentations', 'StimulationMaps', 'ElectrodeModel', 'Other']
        self.combobox_file_type.addItems(file_type_options)
        self.combobox_file_type.currentIndexChanged.connect(self.add_file_type)
        layout_v2.addWidget(self.combobox_file_type)

        # Text field where the user can type the additional file type
        self.text_file_type = QLineEdit(self)
        self.text_file_type.setPlaceholderText('Specify file type')
        self.text_file_type.setVisible(False)
        layout_v2.addWidget(self.text_file_type)

        # Text field where the user can type the reference space of the file (for transformed files)
        self.text_space = QLineEdit(self)
        self.text_space.setPlaceholderText('Specify reference space')
        layout_v2.addWidget(self.text_space)

        # Text field where the user can type the subject acronym(s)
        self.text_subj_acr = QLineEdit(self)
        self.text_subj_acr.setPlaceholderText('Indicate subject acronym(s)')
        layout_v3.addWidget(self.text_subj_acr)

        # Text field where the user can type the session(s)
        self.text_session = QLineEdit(self)
        self.text_session.setPlaceholderText('Indicate session(s)')
        layout_v3.addWidget(self.text_session)

        # Text field where the user can type the acquisition(s)
        self.text_acquisition = QLineEdit(self)
        self.text_acquisition.setPlaceholderText('Indicate acquisition(s)')
        layout_v3.addWidget(self.text_acquisition)

        # Text field where the user can type the file(s) name(s)
        self.text_file_name = QLineEdit(self)
        self.text_file_name.setPlaceholderText('Indicate file(s) name(s)')
        layout_v3.addWidget(self.text_file_name)

        # Label for suffix
        self.suffix_label = QLabel('Choose suffix: ', self)
        layout_v3.addWidget(self.suffix_label)

        # Combo box with choices of suffixes - if the user chooses other he can type
        self.combobox_suffix = QComboBox(self)
        suffix_options = ['T1w', 'T2star', 'FLAIR', 'vtkLine', 'TrajTransform', 'comsolmodel',
                   'matrix', 'coordinates', 'warp', 'mesh', 'label', 'image', 'Other']
        self.combobox_suffix.addItems(suffix_options)
        self.combobox_suffix.currentIndexChanged.connect(self.add_suffix)
        layout_v3.addWidget(self.combobox_suffix)

        # Text field where the user can type the additional suffix
        self.text_suffix = QLineEdit(self)
        self.text_suffix.setPlaceholderText('Specify suffix')
        self.text_suffix.setVisible(False)
        layout_v3.addWidget(self.text_suffix)

        # Button to generate BIDS-compliant file paths
        self.gen_bids_button = QPushButton('Convert files', self)
        self.gen_bids_button.clicked.connect(self.convert_to_bids) 
        layout_h2.addWidget(self.gen_bids_button)

        # Label to show converted file names
        self.bids_file_label = QLabel('Proposed names: ', self)
        self.bids_file_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Scrollable area in which to embed the bids files names label - we expect the text to be long if many files are selected
        self.bids_files_scroll_area = QScrollArea(self)
        self.bids_files_scroll_area.setWidgetResizable(True)
        self.bids_files_scroll_area.setWidget(self.bids_file_label)
        self.bids_files_scroll_area.setFixedSize(1000, 200)
        layout_h2.addWidget(self.bids_files_scroll_area)

        layout_h2.setStretch(1,3)

        # Button to move files from original folder to BIDS folder with renaming
        self.move_files_button = QPushButton('Move files', self)
        self.move_files_button.clicked.connect(self.move_files) 
        layout_h3.addWidget(self.move_files_button)

        # Button to copy files from original folder to BIDS folder, keeping also the original ones
        self.copy_files_button = QPushButton('Copy files', self)
        self.copy_files_button.clicked.connect(self.copy_files) 
        layout_h3.addWidget(self.copy_files_button)

        # Button to open application for json files generation
        self.gen_json_button = QPushButton('Generate sidecars', self)
        self.gen_json_button.clicked.connect(self.open_json_generator) 
        layout_h3.addWidget(self.gen_json_button)

        # Label with FHNW logo
        image_label = QLabel(self)
        pixmap = QPixmap('./fhnw_logo.png') 
        pixmap = pixmap.scaled(200, 50, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        image_label.setMaximumSize(200,50)
        layout_h3.addWidget(image_label, 0, alignment=Qt.AlignmentFlag.AlignRight)

        # Separation lines
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)

        line3 = QFrame()
        line3.setFrameShape(QFrame.Shape.HLine)
        line3.setFrameShadow(QFrame.Shadow.Sunken)

        line4 = QFrame()
        line4.setFrameShape(QFrame.Shape.VLine)
        line4.setFrameShadow(QFrame.Shadow.Sunken)

        line5 = QFrame()
        line5.setFrameShape(QFrame.Shape.VLine)
        line5.setFrameShadow(QFrame.Shadow.Sunken)

        layout_h4.addLayout(layout_v1)
        layout_h4.addWidget(line4)
        layout_h4.addLayout(layout_v2)
        layout_h4.addWidget(line5)
        layout_h4.addLayout(layout_v3)

        layout_v4.addLayout(layout_h0)
        layout_v4.addWidget(line1)
        layout_v4.addLayout(layout_h4)
        layout_v4.addWidget(line2)
        layout_v4.addLayout(layout_h2)
        layout_v4.addWidget(line3)
        layout_v4.addLayout(layout_h3)

        self.setLayout(layout_v4)

        self.init_widgets()

        # Set theme, fonts and style of window
        self.setStyleSheet("""
            QWidget {
                background-color: #bec3c8;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #fff48d;
                color: black;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #fbd100;
            }
            QLabel, QLineEdit, QCheckBox, QComboBox {
                font-size: 14px;
                color: black;
            }
            QLineEdit {
                background-color: white;
                color: #333;
            }
        """)

        # Define buttons max size
        self.set_button_size(150, 40)

        # When the application is started the window is full screen
        self.showMaximized()
   
    def init_widgets(self):
        """
        Function setting all the GUI widgets to initial state
        """
        self.add_file_button.setDisabled(True)
        self.clear_button.setDisabled(True)
        self.file_label.setText('Selected files: ')
        self.bids_folder_label.setText('Select BIDS folder ')
        self.checkbox_derivative.setChecked(False)
        self.checkbox_derivative.setCheckable(False)
        self.combobox_subj_type.setCurrentIndex(0)
        self.combobox_subj_type.setEnabled(False)
        self.combobox_file_type.setCurrentIndex(-1)
        self.combobox_file_type.setEnabled(False)
        self.text_file_type.clear()
        self.text_file_type.setVisible(False)
        self.text_space.clear()
        self.text_space.setEnabled(False)
        self.text_subj_acr.clear()
        self.text_subj_acr.setEnabled(False)
        self.text_session.clear()
        self.text_session.setEnabled(False)
        self.text_acquisition.clear()
        self.text_acquisition.setEnabled(False)
        self.text_file_name.clear()
        self.text_file_name.setEnabled(False)
        self.combobox_suffix.setCurrentIndex(-1)
        self.combobox_suffix.setEnabled(False)
        self.text_suffix.clear()
        self.text_suffix.setVisible(False)
        self.move_files_button.setDisabled(True)
        self.copy_files_button.setDisabled(True)
        self.gen_json_button.setDisabled(True)
        self.gen_bids_button.setDisabled(True)
        self.bids_file_label.setText('Proposed names: ')

    def set_button_size(self, width, height):
        """
        Function to set maximum button size
        """
        for widget in self.findChildren(QPushButton):
            widget.setMaximumSize(width, height)
 
    def select_folder(self):
        """
        Function to select BIDS project folder in which the files need to be transferred. The BIDS folder path is saved in bids_folder
        and is updated every time that the button is activated (we can have only one folder). After the folder has been selected the 
        button "Add file" is activated
        """
        global bids_folder
        bids_folder = ""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", "", options=QFileDialog.Option.ShowDirsOnly|QFileDialog.Option.DontUseNativeDialog)
        if folder_path:
            bids_folder = folder_path
            self.bids_folder_label.setText(f"Selected folder: {folder_path}")
            self.bids_folder_label.setWordWrap(True)
            self.add_file_button.setDisabled(False)
        else:
            self.bids_folder_label.setText('Select BIDS folder ')
    
    def select_multiple_files(self):
        """
        Function to select one or more files by browsing folders. Every time that the function is called
        the newly selected files are added to the original_files_list list. The whole file list is displayed below the 
        Add files button. If at least one file has been selected the rest of the GUI fields are enabled
        """
        global original_files_list
        filenames, _ = QFileDialog.getOpenFileNames(self, options= QFileDialog.Option.DontUseNativeDialog)
        # If some files have been selected
        if filenames:
            for i in range(len(filenames)):
                # If the filename is not already in the list
                if filenames[i] not in original_files_list:
                    original_files_list.extend(filenames)
            self.unlock_gui(original_files_list)
    
    def unlock_gui(self, list):
        """
        Function to unlock the other GUI fields after some files have been selected
        """
        self.file_label.setText('Selected files:\n'+'\n\n'.join(list))
        self.file_label.setWordWrap(True)
        self.clear_button.setDisabled(False)
        self.checkbox_derivative.setCheckable(True)
        self.combobox_file_type.setEnabled(True)
        self.text_subj_acr.setEnabled(True)
        self.text_session.setEnabled(True)
        self.text_acquisition.setEnabled(True)
        self.text_file_name.setEnabled(True)
        self.combobox_suffix.setEnabled(True)
        self.gen_bids_button.setEnabled(True) 
    
    def clear_files(self):
        """
        Function to clear the file list and reset the GUI to initialization status
        """
        global original_files_list, bids_files_list
        original_files_list = []
        bids_files_list = []
        self.init_widgets()
    
    def toggle_der_inputs(self):
        """
        Function enabling the derivative-related fields when derivative checkbox is checked and disabling them
        when it is not checked
        """
        if self.checkbox_derivative.isChecked():
            self.combobox_subj_type.setDisabled(False)
            self.text_space.setDisabled(False)
        else:
            self.combobox_subj_type.setDisabled(True)
            self.text_space.setDisabled(True)
    
    def add_file_type(self, index):
        """
        Function to show the text field in which the user can type a new file type not present in the combobox list. The text field
        is shown when the option 'Other' is selected in the combobox
        """
        if self.combobox_file_type.currentText() == 'Other':
            self.text_file_type.setVisible(True)
        else:
            self.text_file_type.setVisible(False)
            self.text_file_type.clear()

    def add_suffix(self, index):
        """
        Function to show the text field in which the user can type a new suffix not present in the combobox list. The text field
        is shown when the option 'Other' is selected in the combobox
        """
        if self.combobox_suffix.currentText() == 'Other':
            self.text_suffix.setVisible(True)
        else:
            self.text_suffix.setVisible(False)
            self.text_suffix.clear()
    
    def convert_to_bids(self):
        """
        Function to generate the BIDS-compliant names, save them in a list and show them in the label. If the file is a derivative and 
        the space field is populated the space parameter is also added to the name.

        Multiple files can be processed at the same time. The files need to have the same subject_type, file_type and suffix. They can have
        different subject acronyms, sessions, acquisitions, file names and spaces. To do so, the user needs to provide a list of values 
        (separated by commas with no spaces) in the respective text fields. If k is the number of selected files the application accepts:
            - one value provided in the text field --> all the files will get the same value
            - k values provided in the text field --> each value is associated to a file 
                - NOTE: order is important: the first value must refer to the first file and so on
        """
        global bids_folder, original_files_list, bids_files_list
        bids_files_list = []

        # Get number of selected files
        n_orig_files = len(original_files_list)

        # Get the text typed by the user in case of choice of Other from combobox
        if self.combobox_suffix.currentText()=='Other':
            suffix = self.text_suffix.text()
        else:
            suffix = self.combobox_suffix.currentText()
        if self.combobox_file_type.currentText()=='Other':
            file_type = self.text_file_type.text()
        else:
            file_type = self.combobox_file_type.currentText()
        
        # Get file extension from original file name
        original_file_name = original_files_list[0]
        ext = original_file_name.split('.')[-1]
        # Get the inputs from GUI
        subj_acr = self.text_subj_acr.text().split(',')
        session = self.text_session.text().split(',')
        acquisition = self.text_acquisition.text().split(',')
        file_name = self.text_file_name.text().split(',')

        fields_to_check = [subj_acr, session, acquisition, file_name]
        fields_to_check_names = ["subject acronym", "session", "acquisition", "file name"]
    
        # Check that the suffix and file type fields are not empty
        if (suffix.strip() and file_type.strip()):
            # Check that the subj_acr, session, acquisition, file name fields have either 1 or n_orig_files element(s)
            for j in range(len(fields_to_check)):
                if ((len(fields_to_check[j]) != 1) and (len(fields_to_check[j]) != n_orig_files)):
                    QMessageBox.information(self, "Error", f"You provided {len(fields_to_check[j])} {fields_to_check_names[j]}. Please provide 1 or {n_orig_files}")
                    return
                # If there is only one value provided multiply the value to create list
                if (len(fields_to_check[j]) == 1):
                    fields_to_check[j] = fields_to_check[j] * n_orig_files
            subj_acr = fields_to_check[0]
            session = fields_to_check[1]
            acquisition = fields_to_check[2]
            file_name = fields_to_check[3]

            # If we have a derivative
            if self.checkbox_derivative.isChecked():
                subj_type = self.combobox_subj_type.currentText()
                space = self.text_space.text().split(',')
                # Compose the BIDS derivative file path
                deriv_folder = f"{bids_folder}/derivatives"
                # Check that the number of space elements is 0, 1 or n_orig_files
                if ((len(space) != 1) and (len(space) != n_orig_files) and (len(space) != 0)):
                    QMessageBox.information(self, "Error", f"You provided {len(space)} spaces. Please provide 0, 1 or {n_orig_files}")
                else:
                    # If there is only one space provided multiply the value to create list
                    if (len(space)==1):
                        space = space * n_orig_files
                    # Loop through the original files and generate new names
                    for i in range(n_orig_files):
                        # Get file extension from original file name
                        ext = original_files_list[i].split('.',1)[1]
                        if (space[i] != '' and space[i] != ' '):
                            deriv_file_name = f"sub-{subj_acr[i]}_space-{space[i]}_ses-{session[i]}_acq-{acquisition[i]}_{file_name[i]}_{suffix}.{ext}"
                        else:
                            deriv_file_name = f"sub-{subj_acr[i]}_ses-{session[i]}_acq-{acquisition[i]}_{file_name[i]}_{suffix}.{ext}"
                        file_path = f"{deriv_folder}/{subj_type}/sub-{subj_acr[i]}/{file_type}/{deriv_file_name}"
                        # Add newly generated file path to list 
                        bids_files_list.append(file_path)
            
            # If it's not a derivative
            else:
                # Loop through the original files and generate new names
                for i in range(n_orig_files):
                    # Get file extension from original file name
                    ext = original_files_list[i].split('.',1)[1]
                    raw_file_name = f"sub-{subj_acr[i]}_ses-{session[i]}_acq-{acquisition[i]}_{file_name[i]}_{suffix}.{ext}"
                    file_path = f"{bids_folder}/sub-{subj_acr[i]}/ses-{session[i]}/{file_type}/{raw_file_name}"
                    # Add newly generated file path to list 
                    bids_files_list.append(file_path)
            # Print generated file paths in label
            self.bids_file_label.setText('Proposed names:\n'+'\n'.join(bids_files_list))
            # Unlock buttons for next actions
            self.move_files_button.setEnabled(True)
            self.copy_files_button.setEnabled(True)
        # If suffix or file type hasn't been completed show error dialog
        else:
            QMessageBox.information(self, "Error", f"Please provide a suffix and a file type to enable BIDS file name generation")
    
    def move_files(self):
        """
        Function to move files to new BIDS destination. The original files are deleted. If the BIDS destination folder does not exist it is created
        If file already exists at destination folder it asks permission before overwriting. 
        """
        global original_files_list, bids_files_list
        moved_files = 0 # Counter to keep count of successfully moved files
        for old_path, new_path in zip(original_files_list, bids_files_list):
            new_dir = os.path.dirname(new_path)
            
            # Create the destination directory if it doesn't exist
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)

            # Check if the file at new_path already exists
            if os.path.exists(new_path):
                # Create a QMessageBox for confirmation
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Icon.Question)
                msg_box.setText(f"The file {new_path} already exists. Do you want to overwrite it?")
                msg_box.setWindowTitle("Confirm Overwrite")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                
                response = msg_box.exec()
                
                if response == QMessageBox.StandardButton.No:
                    # If the user clicks "No", skip this file and drop it from the list passed to the json generator
                    bids_files_list.remove(new_path)
                    continue
                else:
                    shutil.move(old_path, new_path)
                    moved_files = moved_files + 1
            else:
                # Move the file from old_path to new_path
                shutil.move(old_path, new_path)
                moved_files = moved_files + 1
        
        # If at least one file has been moved generate success dialog and enable passing to json generator.
        # The file paths passed to the json generator are only the ones for which moving was allowed by the user
        if moved_files>0:
            # Enable button to pass to json generator
            self.gen_json_button.setEnabled(True)
            # Success dialog at the end
            QMessageBox.information(self, "Information", f"The files have been successfully moved and renamed.\
                                    \nClick on Generate sidecars to open the sidecar generator app or on Clear to process another file batch.\
                                    \nOnly the moved files will be passed to the json generator")

    
    def copy_files(self):
        """
        Function to copy files to new BIDS destination. The original files are kept. If the BIDS destination folder does not exist it is created
        If the destination file already exists ask permission before overwriting
        """
        global original_files_list, bids_files_list
        moved_files = 0 # Counter to keep count of successfully moved files
        for old_path, new_path in zip(original_files_list, bids_files_list):
            new_dir = os.path.dirname(new_path)
            
            # Create the destination directory if it doesn't exist
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)

            # Check if the file at new_path already exists
            if os.path.exists(new_path):
                # Create a QMessageBox for confirmation
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Icon.Question)
                msg_box.setText(f"The file {new_path} already exists. Do you want to overwrite it?")
                msg_box.setWindowTitle("Confirm Overwrite")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                
                response = msg_box.exec()
                
                if response == QMessageBox.StandardButton.No:
                    # If the user clicks "No", skip this file and drop it from the list passed to the json generator
                    bids_files_list.remove(new_path)
                    continue
                else:
                    shutil.copy2(old_path, new_path)
                    moved_files = moved_files + 1
            else:
                # Move the file from old_path to new_path
                shutil.copy2(old_path, new_path)
                moved_files = moved_files + 1
        # If at least one file has been moved generate success dialog and enable passing to json generator.
        # The file paths passed to the json generator are only the ones for which moving was allowed by the user
        if moved_files>0:
            # Enable button to pass to json generator
            self.gen_json_button.setEnabled(True)
            # Success dialog at the end
            QMessageBox.information(self, "Information", f"The files have been successfully copied and renamed. \
                                    \nClick on Generate sidecars to open the sidecar generator app or on Clear to process another file batch\
                                    \nOnly the moved files will be passed to the json generator")
    
    def open_json_generator(self):
        """
        Function to open the application which generates json sidecar files and close the current one. The newly generated BIDS-compliant
        file names are passed as input to the json generator 
        """
        global bids_files_list
        # Ask for confirmation before closing app and passing to the other one
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle("Confirm Action")
        msg_box.setText("The BIDS converter will be closed and the json generator will be activated. Proceed?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        response = msg_box.exec()
        if response == QMessageBox.StandardButton.Yes:
            # Serialize the list to a JSON string
            list_of_strings_json = json.dumps(bids_files_list)
            # Open the second app by running the second script with the JSON string as an argument
            subprocess.Popen(['BIDSsidecar_file_creator.exe', list_of_strings_json])
            # Close the current app
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BIDSConverter()
    ex.show()
    sys.exit(app.exec())