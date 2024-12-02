"""
Script for a GUI allowing to generate BIDS-compliant json sidecar files for one or more selected files. 
Part of the information to be added to the sidecar file is automatically extracted from the file name and path
and part has to be manually inserted by the user thorugh the GUI.
***The input files need to be already named and organized according to BIDS

The structure of the json files is shown in the sample_sidecar_file.json

The application can also be started after closing the BIDS converter. In this case the paths of the files
moved into the BIDS folder are already passed as input. Additional files can be added with the "Add files" button
"""

import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QProgressDialog,
    QLineEdit, QCheckBox, QLabel, QMessageBox, QDateEdit, QFrame, QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
import gui_functions as gf

file_list:list
file_list = [] # Variable in which to save the list of absolute file paths
info_dict_list:list
info_dict_list = [] # List of dictionaries with information extracted from file name - needed when processing multiple files together
source_ids = [] # Hash of source file - only for transformed files  
target_id = "" # Hash of target file - only for transformed files 
warp_id = "" # Hash of warp file - only for transformed files

class HashGenThread(QThread):
    # Define signals to communicate with the main thread
    progress = pyqtSignal(int)  # Signal for progress update
    finished = pyqtSignal(list)  # Signal when processing is finished

    def __init__(self, files):
        super().__init__()
        self.files = files  # Files to process

    def run(self):
        global source_ids
        total_files = len(self.files)
        # Perform the hash calculation 
        for idx, file in enumerate(self.files):
            # Calculate hash for the file (simulate a long-running task)
            source_id = gf.calculate_hash(file)
            source_ids.append(source_id)
            # Update the progress bar by emitting the current progress (percentage of completed files)
            self.progress.emit(int((idx + 1) / total_files * 100))  # Progress percentage

        # Once done, emit the result (list of source_ids)
        self.finished.emit(self.files)

class ExtractionThread(QThread):
    # Signal to update progress bar with the progress percentage
    progress = pyqtSignal(int)  
    # Signal to indicate that the thread has finished processing
    finished = pyqtSignal()  

    def __init__(self, file_list, label, transformed):
        super().__init__()
        # Initialize the class with the necessary data: list of files, label flag, and transformed flag
        self.file_list = file_list
        self.label = label
        self.transformed = transformed

    def run(self):
        global info_dict_list
        # Get the total number of files to process
        total_files = len(self.file_list)
        # Clear previous information to prevent overwriting
        info_dict_list = [] 
        for idx, file_abs_path in enumerate(self.file_list):
            # Extract information from the current file (this will depend on the logic in `extract_info_from_filename`)
            info_dict = gf.extract_info_from_filename(str(file_abs_path), is_label=self.label, is_transformed=self.transformed)
            # Append the extracted info to the global list
            info_dict_list.append(info_dict)
            # Update the progress bar by emitting the current progress (percentage of completed files)
            self.progress.emit(int((idx + 1) / total_files * 100))  # Progress percentage
        # Once all files have been processed, emit the finished signal
        self.finished.emit()

class SidecarGenerator(QWidget):
    def __init__(self, list_of_files = []):
        super().__init__()
        global file_list
        
        # This list of files can be passed by the BIDS converter app 
        file_list = list_of_files

        self.initUI()

    def initUI(self):
        global file_list
        self.setWindowTitle("Sidecar file generator")

        layout_v1 = QVBoxLayout() # For select button and selected files label
        layout_v1.setContentsMargins(10, 10, 10, 10)
        layout_v1.setSpacing(20)
        layout_v2 = QVBoxLayout() # For label checkbox, color and comment text field
        layout_v2.setContentsMargins(10, 10, 10, 10)
        layout_v3 = QVBoxLayout() # For transformation checkbox, identity checkbox, source, target and transform files
        layout_v3.setContentsMargins(10, 10, 10, 10)
        layout_v3.setSpacing(10)
        layout_v4 = QVBoxLayout() # For info extraction button and outcome message
        layout_v4.setContentsMargins(10, 10, 10, 10)
        layout_v5 = QVBoxLayout() # For modality, protocol and DICOM image type text fields
        layout_v5.setContentsMargins(10, 10, 10, 10)
        layout_v6 = QVBoxLayout() # For acquisition date box and stereotactic checkbox
        layout_v6.setContentsMargins(10, 10, 10, 10)
        layout_v7 = QVBoxLayout() # For explanation label, layout_h4, layout_h5 and save button

        layout_h0 = QHBoxLayout() # For add files and clear screen buttons
        layout_h1 = QHBoxLayout() # For source file button and label
        layout_h2 = QHBoxLayout() # For target file button and label
        layout_h3 = QHBoxLayout() # For warp file button and label
        layout_h4 = QHBoxLayout() # For layout_v1, layout_v2, layout_v3
        layout_h5 = QHBoxLayout() # For layout_v4, layout_v5, layout_v6
        layout_h6 = QHBoxLayout() # For save button and FHNW logo
        layout_h7 = QHBoxLayout() # For extract info button and progress bar

        # Label explaining how to use the GUI
        self.explanation_label = QLabel(self)
        self.explanation_label.setText('This application allows to generate BIDS-compliant sidecar files. <br>' 
                                        '1) Start by selecting the file(s) for which the sidecars need to be generated <br> '
                                        '2) Indicate whether the file(s) are labels or transformed files by checking the appropriate boxes <br> '
                                        '3) Fill in the required information <br> '
                                        '4) Click on "Extract information" to trigger automatic extraction of the other sidecar fields <br> '
                                        '5) Click on "Save json" to generate the json file(s) <br> <br> '
                                        '<b>Important notes:</b> <br> '
                                        '-The workflow can be applied <b>ONLY</b> to files named according to BIDS standard <br> '
                                        '-Multiple files can be processed at once if they have the same values of the manually filled fields')
        self.explanation_label.setWordWrap(True)  # Enable text wrapping
        self.explanation_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        # File selection button
        self.add_file_button = QPushButton('Add Files', self)
        self.add_file_button.clicked.connect(self.select_multiple_files)
        layout_h0.addWidget(self.add_file_button)

        # Create the progress bar widget
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        # Clear button
        self.clear_button = QPushButton('Clear', self)
        self.clear_button.clicked.connect(self.clear_files)
        layout_h0.addWidget(self.clear_button)

        layout_v1.addLayout(layout_h0)      
        
        # Label to show selected files
        self.file_label = QLabel('Selected files: ', self)
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Scrollable area in which to embed the selected files label - we expect the text to be long if many files are selected
        self.files_scroll_area = QScrollArea(self)
        self.files_scroll_area.setWidgetResizable(True)
        self.files_scroll_area.setWidget(self.file_label)
        self.files_scroll_area.setFixedSize(500,220)
        layout_v1.addWidget(self.files_scroll_area)

        layout_v1.addStretch()

        # Checkbox to indicate whether the file is a label
        self.checkbox_label = QCheckBox("Is the file a label?", self)
        self.checkbox_label.stateChanged.connect(self.toggle_text_input_label)
        layout_v2.addWidget(self.checkbox_label)
        
        # Text field with label color
        self.text_color = QLineEdit(self)
        self.text_color.setPlaceholderText("Indicate label color:")
        layout_v2.addWidget(self.text_color)

        # Text field with label comment
        self.text_comment = QLineEdit(self)
        self.text_comment.setPlaceholderText("Type comments (for labels)")
        layout_v2.addWidget(self.text_comment)

        layout_v2.addStretch()

        # File selection button - source file
        self.source_file_button = QPushButton('Select source', self)
        self.source_file_button.clicked.connect(self.select_source_file)
        layout_h1.addWidget(self.source_file_button)

        # Label to show selected files - source file
        self.source_file_label = QLabel('Select source files ', self)
        self.source_file_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Scrollable area in which to embed the selected files label - we expect the text to be long if many files are selected
        self.source_files_scroll_area = QScrollArea(self)
        self.source_files_scroll_area.setWidgetResizable(True)
        self.source_files_scroll_area.setWidget(self.source_file_label)
        self.source_files_scroll_area.setFixedSize(500,220)

        # Create the progress bar widget to show processing status of source files hashes
        self.sf_progress_bar = QProgressBar(self)
        self.sf_progress_bar.setRange(0, 100)
        self.sf_progress_bar.setValue(0)
        self.sf_progress_bar.setTextVisible(True)

        # File selection button - target file
        self.target_file_button = QPushButton('Select target', self)
        self.target_file_button.clicked.connect(self.select_target_file)
        layout_h2.addWidget(self.target_file_button)

        # Label to show selected files - target file
        self.target_file_label = QLabel('Select a target file ', self)
        self.target_file_label.setFixedSize(200,100)
        self.target_file_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout_h2.addWidget(self.target_file_label)

        # File selection button - warp file
        self.warp_file_button = QPushButton('Select warp', self)
        self.warp_file_button.clicked.connect(self.select_warp_file)
        layout_h3.addWidget(self.warp_file_button)

        # Label to show selected files - warp file
        self.warp_file_label = QLabel('Select a warp file ', self)
        self.warp_file_label.setFixedSize(200,100)
        self.warp_file_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout_h3.addWidget(self.warp_file_label)

        # Checkbox to indicate whether the file is a transformation
        self.checkbox_transformation = QCheckBox("Was the file transformed?", self)
        self.checkbox_transformation.stateChanged.connect(self.toggle_text_input_transf)
        layout_v3.addWidget(self.checkbox_transformation)

        # Checkbox to indicate whether the transformation is an identity
        self.checkbox_identity = QCheckBox("Was the transformation an identity?", self)
        layout_v3.addWidget(self.checkbox_identity)

        layout_v3.addLayout(layout_h1)
        layout_v3.addWidget(self.sf_progress_bar)
        layout_v3.addWidget(self.source_files_scroll_area)
        layout_v3.addLayout(layout_h2)
        layout_v3.addLayout(layout_h3)
        layout_v3.addStretch()

        # Button to trigger information extraction from file name
        self.extract_info_button = QPushButton('Extract information', self)
        self.extract_info_button.clicked.connect(self.show_dialog_extract)
        layout_h7.addWidget(self.extract_info_button)
        layout_h7.addWidget(self.progress_bar)
        layout_h7.addStretch()
        
        layout_v4.addLayout(layout_h7)

        # Label to show extraction status
        self.extraction_status_label = QLabel('', self)
        layout_v4.addWidget(self.extraction_status_label, 0, Qt.AlignmentFlag.AlignCenter)

        # Text field with file modality
        self.text_modality = QLineEdit(self)
        self.text_modality.setPlaceholderText("Indicate file modality")
        layout_v5.addWidget(self.text_modality)

        # Text field with protocol name
        self.text_protocol = QLineEdit(self)
        self.text_protocol.setPlaceholderText("Indicate protocol name")
        layout_v5.addWidget(self.text_protocol)

        # Text field with DICOM image type
        self.text_dicom_type = QLineEdit(self)
        self.text_dicom_type.setPlaceholderText("Indicate DICOM image type")
        layout_v5.addWidget(self.text_dicom_type)

        # Checkbox to indicate whether the file is stereotactic
        self.checkbox_stereo = QCheckBox("Stereotactic?", self)
        layout_v6.addWidget(self.checkbox_stereo)
        
        # Text field with acquisition date
        # Date picker layout with label
        date_picker_layout = QHBoxLayout()
        self.date_picker_label = QLabel("Select acquisition date:", self)
        self.date_picker = QDateEdit(self)
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        date_picker_layout.addWidget(self.date_picker_label)
        date_picker_layout.addWidget(self.date_picker)
        layout_v6.addLayout(date_picker_layout)

        # Separation lines
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.VLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)

        line3 = QFrame()
        line3.setFrameShape(QFrame.Shape.VLine)
        line3.setFrameShadow(QFrame.Shadow.Sunken)

        line4 = QFrame()
        line4.setFrameShape(QFrame.Shape.HLine)
        line4.setFrameShadow(QFrame.Shadow.Sunken)

        line5 = QFrame()
        line5.setFrameShape(QFrame.Shape.HLine)
        line5.setFrameShadow(QFrame.Shadow.Sunken)

        layout_h4.addLayout(layout_v1, 2)
        layout_h4.addWidget(line2)
        layout_h4.addLayout(layout_v2, 1)
        layout_h4.addWidget(line3)
        layout_h4.addLayout(layout_v3, 1)

        layout_h5.addLayout(layout_v4, 2)
        layout_h5.addLayout(layout_v5, 1)
        layout_h5.addLayout(layout_v6, 1)

        layout_v7.addWidget(self.explanation_label, 0, Qt.AlignmentFlag.AlignTop)
        layout_v7.addWidget(line1)
        layout_v7.addLayout(layout_h4)
        layout_v7.addWidget(line4)
        layout_v7.addLayout(layout_h5)
        layout_v7.addWidget(line5)
        
        # Save button
        self.save_button = QPushButton('Save json', self)
        self.save_button.clicked.connect(self.show_dialog_proceed)
        layout_h6.addWidget(self.save_button, 0, Qt.AlignmentFlag.AlignCenter)

        # Label with FHNW logo
        image_label = QLabel(self)
        pixmap = QPixmap('./fhnw_logo.png') 
        pixmap = pixmap.scaled(200, 50, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        image_label.setMaximumSize(200,50)
        layout_h6.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignRight)

        layout_v7.addLayout(layout_h6)
        self.setLayout(layout_v7)

        # Set widgets to their initial status, some of them are disabled in the beginning
        self.init_widgets()

        self.showMaximized()

        # If the application is started by the BIDS converter the list of files is already passed as input
        if file_list:
            self.unlock_gui(file_list)

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

        # Set stylesheet for progress bar to make it yellow
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid black;
                border-radius: 1px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #fbd100;  
                width: 20px;
            }
        """)

        # Set stylesheet for progress bar to make it yellow
        self.sf_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid black;
                border-radius: 1px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #fbd100;  
                width: 20px;
            }
        """)

        # Define buttons max size
        self.set_button_size(150, 40)

        
    def init_widgets(self):
        """
        Function setting all the GUI widgets to initial state
        """
        self.clear_button.setDisabled(True)
        self.file_label.setText('Selected files: ')
        self.checkbox_label.setChecked(False)
        self.checkbox_label.setCheckable(False)
        self.checkbox_transformation.setChecked(False)
        self.checkbox_transformation.setCheckable(False)
        self.text_color.clear()
        self.text_comment.clear()
        self.text_color.setDisabled(True)
        self.text_comment.setDisabled(True)
        self.source_file_button.setDisabled(True)
        self.target_file_button.setDisabled(True)
        self.warp_file_button.setDisabled(True)
        self.source_file_label.setText('Select a source file ')
        self.target_file_label.setText('Select a target file ')
        self.warp_file_label.setText('Select a warp file ')
        self.checkbox_identity.setCheckable(False)
        self.checkbox_identity.setChecked(False)
        self.checkbox_stereo.setCheckable(False)
        self.checkbox_stereo.setChecked(False)
        self.extract_info_button.setDisabled(True)
        self.extraction_status_label.setText('')
        self.text_modality.setDisabled(True)
        self.text_modality.clear()
        self.text_dicom_type.setDisabled(True)
        self.text_dicom_type.clear()
        self.text_protocol.setDisabled(True)
        self.text_protocol.clear()
        self.date_picker.setDisabled(True)
        self.date_picker.setDate(QDate.currentDate())
        self.save_button.setDisabled(True)
        self.progress_bar.setValue(0)
        self.sf_progress_bar.setValue(0)
    
    def set_button_size(self, width, height):
        """
        Function to set maximum button size
        """
        for widget in self.findChildren(QPushButton):
            widget.setMaximumSize(width, height)

    def toggle_text_input_label(self):
        """
        Function enabling the label-related fields when label checkbox is checked and disabling them
        when it is not checked
        """
        if self.checkbox_label.isChecked():
            self.text_color.setDisabled(False)
            self.text_comment.setDisabled(False)
        else:
            self.text_color.setDisabled(True)
            self.text_comment.setDisabled(True)
    
    def toggle_text_input_transf(self):
        """
        Function enabling the transformation-related fields when transformation checkbox is checked and disabling them
        when it is not checked
        """
        if self.checkbox_transformation.isChecked():
            self.source_file_button.setDisabled(False)
            self.warp_file_button.setDisabled(False)
            self.target_file_button.setDisabled(False)
            self.checkbox_identity.setCheckable(True)
        else:
            self.source_file_button.setDisabled(True)
            self.warp_file_button.setDisabled(True)
            self.target_file_button.setDisabled(True)
            self.checkbox_identity.setCheckable(False)
    
    def select_multiple_files(self):
        """
        Function to select one or more files by browsing folders. Every time that the function is called
        the newly selected files are added to the file_list list. The whole file list is displayed below the 
        Add files button. If at least one file has been selected the rest of the GUI fields are enabled
        """
        global file_list
        filenames, _ = QFileDialog.getOpenFileNames(self)
        if filenames:
            for i in range(len(filenames)):
                # If the filename is not already in the list
                if filenames[i] not in file_list:
                    file_list.extend(filenames)
            self.unlock_gui(file_list)
    
    def unlock_gui(self, list):
        """
        Function to unlock the other GUI fields after some files have been selected
        """
        self.file_label.setText('Selected files:\n'+'\n\n'.join(list))
        self.file_label.setWordWrap(True)
        self.checkbox_stereo.setCheckable(True)
        self.extract_info_button.setDisabled(False)
        self.text_modality.setDisabled(False)
        self.text_dicom_type.setDisabled(False)
        self.text_protocol.setDisabled(False)
        self.date_picker.setDisabled(False)
        self.clear_button.setDisabled(False)
        self.checkbox_transformation.setCheckable(True)
        self.checkbox_label.setCheckable(True)

    def clear_files(self):
        """
        Function to clear the file list and reset the GUI to initialization status
        """
        global file_list, info_dict_list, source_ids, target_id, warp_id
        info_dict_list = []
        file_list = []
        source_ids = []
        target_id = ""
        warp_id = ""
        self.init_widgets()
    
    def select_source_file(self):
        """
        Function to select only one file - the source file for a transformation. The selected file name is 
        shown in the label at the right of the button
        """
        global source_ids, file_list
        source_ids = []
        # Ignore sidecar files
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "VTU and NIFTI Files (*.vtu *.nii *.nii.gz)")
        if files:
            if len(files) == 1 or len(files) == len(file_list):
                # Display a temporary status to indicate processing
                self.source_file_label.setText("Processing selected files, please wait...")
                self.source_file_label.setWordWrap(True)
                
                # Create and start the extraction thread
                self.thread = HashGenThread(files) 
                self.thread.progress.connect(self.update_sf_progress_bar) 
                self.thread.finished.connect(self.on_hashes_done)  # Connect finished signal
                self.thread.start()
            else:
                QMessageBox.warning(self, "Warning", "Please select either: \n1) 1 common source file \n2) As many source files as the input ones")
                self.source_file_label.setText('Select source files')
    
    def update_sf_progress_bar(self, value):
        """
        This function is used to update the progress bar displayed in the GUI. It takes the value parameter, which represents 
        the current progress (typically a percentage from 0 to 100), and sets the progress bar to that value using 
        self.progress_bar.setValue(value). The progress bar visually reflects the current progress of a task, like extracting 
        information from files.
        """
        self.sf_progress_bar.setValue(value)  # Update the progress bar
    
    def on_hashes_done(self, files):
        """Callback to handle the completion of the hashing."""
        self.source_file_label.setText('Selected files:\n' + '\n\n'.join(files))
        self.source_file_label.setWordWrap(True)
    
    def select_target_file(self):
        """
        Function to select only one file - the target file for a transformation. The selected file name is 
        shown in the label at the right of the button
        """
        global target_id
        target_id = ""
        file, _ = QFileDialog.getOpenFileName(self)
        if file:
            target_id = gf.calculate_hash(file)
            self.target_file_label.setText(f"Selected file: {file.split('/')[-1]}")
            self.target_file_label.setWordWrap(True)
        else:
            self.target_file_label.setText('Select a target file')
    
    def select_warp_file(self):
        """
        Function to select only one file - the warp/transform file for a transformation. The selected file name is 
        shown in the label at the right of the button
        """
        global warp_id
        warp_id = ""
        file, _ = QFileDialog.getOpenFileName(self)
        if file:
            warp_id = gf.calculate_hash(file)
            self.warp_file_label.setText(f"Selected file: {file.split('/')[-1]}")
            self.warp_file_label.setWordWrap(True)
        else:
            self.warp_file_label.setText('Select a warp file')

    def extract_info(self):
        """
        Function calling the function which extracts metadata information from the file name and path.
        Depending on whether the label and transformation checkboxes are checked some additional fields are extracted.
        The result is a list of dictionaries (one for each selected file) with all the fields
        """
        global file_list, info_dict_list
        # Empty info_dict_list so that if the extraction needs to be repeated the dictionaries are not duplicated
        info_dict_list = []
        self.progress_bar.setValue(0)
        # Check if the file is a label
        label = False
        transformed = False
        if self.checkbox_label.isChecked():
            label = True
        if self.checkbox_transformation.isChecked():
            transformed = True
        
        # Run extraction in a separate thread
        self.thread = ExtractionThread(file_list, label, transformed)
        self.thread.progress.connect(self.update_progress_bar)  # Connect progress bar update
        self.thread.finished.connect(self.on_extraction_finished)  # Connect completion
        self.thread.start()
    
    def update_progress_bar(self, value):
        """
        This function is used to update the progress bar displayed in the GUI. It takes the value parameter, which represents 
        the current progress (typically a percentage from 0 to 100), and sets the progress bar to that value using 
        self.progress_bar.setValue(value). The progress bar visually reflects the current progress of a task, like extracting 
        information from files.
        """
        self.progress_bar.setValue(value)  # Update the progress bar

    def on_extraction_finished(self):
        """
        This function is called when the extraction process is complete.
        """
        self.extraction_status_label.setText('Information extraction from filename was successful')
        self.save_button.setDisabled(False)  # Enable save button after extraction is done

    def show_dialog_proceed(self):
        """
        Function showing a dialog window asking if the user wants to proceed with the json file generation.
        If the user clicks on No the saving process is stopped
        """
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle("Confirm Action")
        msg_box.setText("Do you want to proceed with the operation?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        response = msg_box.exec()

        if response == QMessageBox.StandardButton.Yes:
            self.saveInformation()
    
    def show_dialog_extract(self):
        """
        Function showing a dialog window asking if the user has filled in the label and transformation fields. Such fields ar read during the
        information extraction of the function extract_info.
        If the user clicks on No the information is not extracted and the user can modify the fields.
        """
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle("Confirm Action")
        msg_box.setText("Please fill in the Label and Transformation information (if applicable) before proceeding.\nProceed?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        response = msg_box.exec()

        if response == QMessageBox.StandardButton.Yes:
            self.extract_info()
    
    
    def saveInformation(self):
        """
        Function generating the JSON file for each selected file. 
        A progress dialog is displayed during the process.
        """
        global file_list, info_dict_list, source_ids, target_id, warp_id

        if not file_list:
            QMessageBox.warning(self, "Warning", "No files to save.")
            return

        # Create a progress dialog
        progress_dialog = QProgressDialog("Saving JSON files...", "Cancel", 0, len(file_list), self)
        progress_dialog.setWindowTitle("Saving Progress")
        progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress_dialog.setValue(0)

        progress_dialog.setStyleSheet("""
            QProgressBar {
                border: 1px solid black;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #fbd100;  /* Yellow */
                width: 10px;
            }
        """)

        for i, file in enumerate(file_list):
            if progress_dialog.wasCanceled():
                QMessageBox.information(self, "Cancelled", "The save operation was canceled.")
                return

            json_path = f"{file.split('.', 1)[0]}_sidecar.json"
            # Fill remaining dictionary fields
            info_dict_list[i]["bids"]["modality"] = self.text_modality.text()
            info_dict_list[i]["bids"]["protocol_name"] = self.text_protocol.text()
            info_dict_list[i]["bids"]["dicom_image_type"] = self.text_dicom_type.text()
            info_dict_list[i]["bids"]["acquisition_date_time"] = self.date_picker.date().toString("dd-MM-yyyy")
            if self.checkbox_stereo.isChecked():
                info_dict_list[i]["bids"]["stereotactic"] = "yes"
            else:
                info_dict_list[i]["bids"]["stereotactic"] = "no"
            if self.checkbox_label.isChecked():
                info_dict_list[i]["labels"]["color"] = self.text_color.text()
                info_dict_list[i]["labels"]["comment"] = self.text_comment.text()
            if self.checkbox_transformation.isChecked():
                info_dict_list[i]["transformations"]["target_id"] = target_id
                info_dict_list[i]["transformations"]["transform_id"] = warp_id
                # If there are multiple source files get the one corresponding to the input file
                if len(source_ids)>1:
                    info_dict_list[i]["files"]["source_id"] = source_ids[i]
                else:
                    info_dict_list[i]["files"]["source_id"] = source_ids[0]
                if self.checkbox_identity.isChecked():
                    info_dict_list[i]["transformations"]["identity"] = "yes"
                else:
                    info_dict_list[i]["transformations"]["identity"] = "no"

            # Save the data to a JSON file
            with open(json_path, "w") as f:
                json.dump(info_dict_list[i], f, indent=4)

            # Update progress dialog
            progress_dialog.setValue(i + 1)

        QMessageBox.information(self, "Information", "The JSON files have been generated successfully.")
        self.clear_files()
        self.init_widgets()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # The application can be called by the BIDS converter app which also sends the list_of_files_json as input
    if len(sys.argv) > 1:
        # Deserialize the list of strings from the command-line argument if provided
        list_of_files_json = sys.argv[1]
        list_of_files = json.loads(list_of_files_json)
    else:
        list_of_files = []
    ex = SidecarGenerator(list_of_files)
    ex.show()
    ex.show()
    sys.exit(app.exec())
