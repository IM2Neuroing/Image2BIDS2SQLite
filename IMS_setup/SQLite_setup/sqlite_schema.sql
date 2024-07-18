CREATE TABLE 
       files 
     ( file_id TEXT NOT NULL
     , subject_id TEXT
     , electrode_id TEXT
     , file_path TEXT NOT NULL
     , file_type TEXT NOT NULL
     , source_id INTEGER
     , transformation_id INTEGER
     , CONSTRAINT fk_images_images_1 FOREIGN KEY (file_id) REFERENCES files (source_id)
     , PRIMARY KEY (file_id)
     , UNIQUE (file_path)
     );

CREATE TABLE 
       bids 
     ( file_id TEXT NOT NULL
     , modality TEXT
     , protocol_name TEXT
     , stereotactic TEXT
     , dicom_image_type TEXT
     , acquisition_date_time TEXT
     , relative_sidecar_path TEXT
     , bids_subject TEXT NOT NULL
     , bids_session TEXT NOT NULL
     , bids_extension TEXT NOT NULL
     , bids_datatype TEXT NOT NULL
     , bids_acquisition TEXT NOT NULL
     , bids_suffix TEXT NOT NULL
     , PRIMARY KEY (file_id)
     , UNIQUE (file_id)
     , CONSTRAINT fk_bids_files_1 FOREIGN KEY (file_id) REFERENCES files (file_id)
     );

CREATE TABLE 
       labels 
     ( file_id TEXT NOT NULL
     , hemisphere TEXT NOT NULL
     , structure TEXT NOT NULL
     , color TEXT
     , comment TEXT
     , PRIMARY KEY (file_id)
     , UNIQUE (file_id)
     , CONSTRAINT fk_labels_files_1 FOREIGN KEY (file_id) REFERENCES files (file_id)
     );

CREATE TABLE 
       transformations 
     ( transformation_id INTEGER PRIMARY KEY AUTOINCREMENT
     , identity TEXT
     , target_id TEXT NOT NULL
     , transform_id TEXT NOT NULL
     , CONSTRAINT fk_transformations_images_2 FOREIGN KEY (target_id) REFERENCES files (file_id)
     , CONSTRAINT fk_transformations_transformations_1 FOREIGN KEY (transform_id) REFERENCES files (file_id)
     , UNIQUE (target_id, transform_id)
     );