INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('4a99e3c4a258f99290f6c5efbd7e89e6afe5ce69d33478751a6e8b5895cee374', 6.0, 'None', 'sub-01SP45MAAAA/ses-Pre/anat/sub-01SP45MAAAA_ses-Pre_acq-aaa_Reference-T1_T1w.nii.gz', 'anat', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('4a99e3c4a258f99290f6c5efbd7e89e6afe5ce69d33478751a6e8b5895cee374', 'MR T1', 'protocol', 'yes', 'None', '06-03-2024', 'sub-01SP45MAAAA/ses-Pre/anat/sub-01SP45MAAAA_ses-Pre_acq-aaa_Reference-T1_T1w_sidecar.json', '01SP45MAAAA', 'Pre', 'nii.gz', 'NifTI', 'aaa', 'T1w');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('2247a0d05777c679527f99471063ed76db697e6bb313440420ee0ff70034655b', NULL, 'None', 'derivatives/Atlases/sub-atlas001/StimulationMaps/sub-atlas001_ses-PD25_acq-acqAtlas_StimPosMap_volume.nii.gz', 'StimulationMaps', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('2247a0d05777c679527f99471063ed76db697e6bb313440420ee0ff70034655b', 'None', 'None', 'no', 'None', '10-07-2024', 'derivatives/Atlases/sub-atlas001/StimulationMaps/sub-atlas001_ses-PD25_acq-acqAtlas_StimPosMap_volume_sidecar.json', 'atlas001', 'PD25', 'nii.gz', 'NifTI', 'acqAtlas', 'volume');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('3ee19e8c166551620f4a612e5c10486fdb295f98aa038f350a2054be0ded617b', NULL, 'None', 'derivatives/Atlases/sub-atlas001/Segmentations/sub-atlas001_ses-PD25_acq-acqAtlas_L-Thal_label.nii.gz', 'Segmentations', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('3ee19e8c166551620f4a612e5c10486fdb295f98aa038f350a2054be0ded617b', 'None', 'None', 'no', 'None', '10-07-2024', 'derivatives/Atlases/sub-atlas001/Segmentations/sub-atlas001_ses-PD25_acq-acqAtlas_L-Thal_label_sidecar.json', 'atlas001', 'PD25', 'nii.gz', 'NifTI', 'acqAtlas', 'label');
INSERT OR IGNORE INTO labels (file_id, hemisphere, structure, color, comment) VALUES ('3ee19e8c166551620f4a612e5c10486fdb295f98aa038f350a2054be0ded617b', 'L', 'Thal', 'yellow', 'None');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('5d83d486e2b3d935b41636cbd15fc0f078ace77a6a81b0659dd14fb06ebe565c', NULL, 'None', 'derivatives/Atlases/sub-atlas001/anat/sub-atlas001_ses-PD25_acq-acqAtlas_template_T2star.mnc.gz', 'anat', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('5d83d486e2b3d935b41636cbd15fc0f078ace77a6a81b0659dd14fb06ebe565c', 'MR T2', 'None', 'no', 'None', '10-07-2024', 'derivatives/Atlases/sub-atlas001/anat/sub-atlas001_ses-PD25_acq-acqAtlas_template_T2star_sidecar.json', 'atlas001', 'PD25', 'mnc.gz', 'Unknown', 'acqAtlas', 'T2star');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('09366b52a2c5c283c0907c959be65399f70582a6e37ff327d2fe36e2d0c01d30', 6.0, 'None', 'derivatives/Patients/sub-01SP45MAAAA/Segmentations/sub-01SP45MAAAA_ses-session_acq-acqLabel_L-Vim_label.nii.gz', 'Segmentations', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('09366b52a2c5c283c0907c959be65399f70582a6e37ff327d2fe36e2d0c01d30', 'MR', 'protocolLabel', 'no', 'None', '10-07-2024', 'derivatives/Patients/sub-01SP45MAAAA/Segmentations/sub-01SP45MAAAA_ses-session_acq-acqLabel_L-Vim_label_sidecar.json', '01SP45MAAAA', 'session', 'nii.gz', 'NifTI', 'acqLabel', 'label');
INSERT OR IGNORE INTO labels (file_id, hemisphere, structure, color, comment) VALUES ('09366b52a2c5c283c0907c959be65399f70582a6e37ff327d2fe36e2d0c01d30', 'L', 'Vim', 'red', 'None');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('f17f0d87a2898c5c006fdd310d731eaf2439ef73ccf2da8280097eaa62269871', 6.0, 'None', 'derivatives/Patients/sub-01SP45MAAAA/Segmentations/sub-01SP45MAAAA_ses-session_acq-acqLabel_R-Thal_label.nii.gz', 'Segmentations', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('f17f0d87a2898c5c006fdd310d731eaf2439ef73ccf2da8280097eaa62269871', 'MR', 'protocolLabel', 'no', 'None', '10-07-2024', 'derivatives/Patients/sub-01SP45MAAAA/Segmentations/sub-01SP45MAAAA_ses-session_acq-acqLabel_R-Thal_label_sidecar.json', '01SP45MAAAA', 'session', 'nii.gz', 'NifTI', 'acqLabel', 'label');
INSERT OR IGNORE INTO labels (file_id, hemisphere, structure, color, comment) VALUES ('f17f0d87a2898c5c006fdd310d731eaf2439ef73ccf2da8280097eaa62269871', 'R', 'Thal', 'red', 'None');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('04a5cf9afd133f94f89d867da379896f1bab9a042a994212ff9d6b6e9b6b1255', 7.0, 'None', 'derivatives/Patients/sub-02ST80FBBBB/Segmentations/sub-02ST80FBBBB_ses-session_acq-acqLabel_L-Zi_label.nii.gz', 'Segmentations', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('04a5cf9afd133f94f89d867da379896f1bab9a042a994212ff9d6b6e9b6b1255', 'MR', 'protocolLabel', 'no', 'None', '10-07-2024', 'derivatives/Patients/sub-02ST80FBBBB/Segmentations/sub-02ST80FBBBB_ses-session_acq-acqLabel_L-Zi_label_sidecar.json', '02ST80FBBBB', 'session', 'nii.gz', 'NifTI', 'acqLabel', 'label');
INSERT OR IGNORE INTO labels (file_id, hemisphere, structure, color, comment) VALUES ('04a5cf9afd133f94f89d867da379896f1bab9a042a994212ff9d6b6e9b6b1255', 'L', 'Zi', 'red', 'None');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('170a6f1c89b461f804e607d7354e0807ea3f9a052be65716a2dac1d99dbadd96', 7.0, 'None', 'derivatives/Patients/sub-02ST80FBBBB/PatientInAtlas/sub-02ST80FBBBB_space-PD25_ses-session_acq-acqLabel_L-Zi_label.nii.gz', 'PatientInAtlas', '04a5cf9afd133f94f89d867da379896f1bab9a042a994212ff9d6b6e9b6b1255', 1);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('170a6f1c89b461f804e607d7354e0807ea3f9a052be65716a2dac1d99dbadd96', 'None', 'None', 'no', 'None', '10-07-2024', 'derivatives/Patients/sub-02ST80FBBBB/PatientInAtlas/sub-02ST80FBBBB_space-PD25_ses-session_acq-acqLabel_L-Zi_label_sidecar.json', '02ST80FBBBB', 'session', 'nii.gz', 'NifTI', 'acqLabel', 'label');
INSERT OR IGNORE INTO labels (file_id, hemisphere, structure, color, comment) VALUES ('170a6f1c89b461f804e607d7354e0807ea3f9a052be65716a2dac1d99dbadd96', 'L', 'Zi', 'red', 'None');
INSERT OR IGNORE INTO transformations (transformation_id, identity, target_id, transform_id) VALUES (1, 'no', '5d83d486e2b3d935b41636cbd15fc0f078ace77a6a81b0659dd14fb06ebe565c', 'd964207a84cdbcf6a8d3890e8dab5fbb2cae5118aa84a91c45d0a1567de9eaa5');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('d964207a84cdbcf6a8d3890e8dab5fbb2cae5118aa84a91c45d0a1567de9eaa5', 7.0, 'None', 'derivatives/Patients/sub-02ST80FBBBB/Transforms/sub-02ST80FBBBB_ses-sesWarp_acq-acqWarp_Patient2PD25_warp.nii.gz', 'Transforms', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('d964207a84cdbcf6a8d3890e8dab5fbb2cae5118aa84a91c45d0a1567de9eaa5', 'None', 'None', 'no', 'None', '10-07-2024', 'derivatives/Patients/sub-02ST80FBBBB/Transforms/sub-02ST80FBBBB_ses-sesWarp_acq-acqWarp_Patient2PD25_warp_sidecar.json', '02ST80FBBBB', 'sesWarp', 'nii.gz', 'NifTI', 'acqWarp', 'warp');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('52be8209965280a123b12e45c743fdf2b8e6260ea3994ed73713fad156f5ad11', 8.0, 'None', 'derivatives/Patients/sub-03SP63MCCCC/Segmentations/sub-03SP63MCCCC_ses-session_acq-acqLabel_R-STN_label.nii.gz', 'Segmentations', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('52be8209965280a123b12e45c743fdf2b8e6260ea3994ed73713fad156f5ad11', 'MR', 'protocolLabel', 'no', 'None', '10-07-2024', 'derivatives/Patients/sub-03SP63MCCCC/Segmentations/sub-03SP63MCCCC_ses-session_acq-acqLabel_R-STN_label_sidecar.json', '03SP63MCCCC', 'session', 'nii.gz', 'NifTI', 'acqLabel', 'label');
INSERT OR IGNORE INTO labels (file_id, hemisphere, structure, color, comment) VALUES ('52be8209965280a123b12e45c743fdf2b8e6260ea3994ed73713fad156f5ad11', 'R', 'STN', 'red', 'None');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('a7ae4ec9bdce90d8befb65063e84219cad62f6b8cb89e4ecf4bc16b18bab60e7', 9.0, 'None', 'derivatives/Patients/sub-04ST71MDDDD/Segmentations/sub-04ST71MDDDD_ses-session_acq-acqLabel_L-CGL_label.nii.gz', 'Segmentations', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('a7ae4ec9bdce90d8befb65063e84219cad62f6b8cb89e4ecf4bc16b18bab60e7', 'MR', 'protocolLabel', 'no', 'None', '10-07-2024', 'derivatives/Patients/sub-04ST71MDDDD/Segmentations/sub-04ST71MDDDD_ses-session_acq-acqLabel_L-CGL_label_sidecar.json', '04ST71MDDDD', 'session', 'nii.gz', 'NifTI', 'acqLabel', 'label');
INSERT OR IGNORE INTO labels (file_id, hemisphere, structure, color, comment) VALUES ('a7ae4ec9bdce90d8befb65063e84219cad62f6b8cb89e4ecf4bc16b18bab60e7', 'L', 'CGL', 'red', 'None');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('b647a9b1acc96d48be6d12e178e9337e8707486f7c0c16746212a7e5dc8a3611', 9.0, 'None', 'derivatives/Patients/sub-04ST71MDDDD/Segmentations/sub-04ST71MDDDD_ses-session_acq-acqLabel_R-Vim_label.nii.gz', 'Segmentations', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('b647a9b1acc96d48be6d12e178e9337e8707486f7c0c16746212a7e5dc8a3611', 'MR', 'protocolLabel', 'no', 'None', '10-07-2024', 'derivatives/Patients/sub-04ST71MDDDD/Segmentations/sub-04ST71MDDDD_ses-session_acq-acqLabel_R-Vim_label_sidecar.json', '04ST71MDDDD', 'session', 'nii.gz', 'NifTI', 'acqLabel', 'label');
INSERT OR IGNORE INTO labels (file_id, hemisphere, structure, color, comment) VALUES ('b647a9b1acc96d48be6d12e178e9337e8707486f7c0c16746212a7e5dc8a3611', 'R', 'Vim', 'red', 'None');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('024545d953ba91e25d6b34a5af0ca0bd10555df765a8254f13692e4cc1c512cd', 7.0, 'None', 'sub-02ST80FBBBB/ses-Pre/anat/sub-02ST80FBBBB_ses-Pre_acq-aaa_Reference-T1_T1w.nii.gz', 'anat', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('024545d953ba91e25d6b34a5af0ca0bd10555df765a8254f13692e4cc1c512cd', 'MR T1', 'protocol', 'yes', 'None', '06-03-2024', 'sub-02ST80FBBBB/ses-Pre/anat/sub-02ST80FBBBB_ses-Pre_acq-aaa_Reference-T1_T1w_sidecar.json', '02ST80FBBBB', 'Pre', 'nii.gz', 'NifTI', 'aaa', 'T1w');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('81920221d6d529c9ffd069d3759b68ce6f9ab536b480d07dbe11926b51a3112a', 8.0, 'None', 'sub-03SP63MCCCC/ses-Pre/anat/sub-03SP63MCCCC_ses-Pre_acq-aaa_Reference-T1_T1w.nii.gz', 'anat', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('81920221d6d529c9ffd069d3759b68ce6f9ab536b480d07dbe11926b51a3112a', 'MR T1', 'protocol', 'yes', 'None', '06-03-2024', 'sub-03SP63MCCCC/ses-Pre/anat/sub-03SP63MCCCC_ses-Pre_acq-aaa_Reference-T1_T1w_sidecar.json', '03SP63MCCCC', 'Pre', 'nii.gz', 'NifTI', 'aaa', 'T1w');
INSERT OR IGNORE INTO files (file_id, subject_id, electrode_id, file_path, file_type, source_id, transformation_id) VALUES ('acf30bc858021abdeee66a42b9d60df0fec07ee1522e3de2fde29c9c635a4a5f', 9.0, 'None', 'sub-04ST71MDDDD/ses-Pre/anat/sub-04ST71MDDDD_ses-Pre_acq-acq_Reference-T2star_T2star.nii.gz', 'anat', 'None', NULL);
INSERT OR IGNORE INTO bids (file_id, modality, protocol_name, stereotactic, dicom_image_type, acquisition_date_time, relative_sidecar_path, bids_subject, bids_session, bids_extension, bids_datatype, bids_acquisition, bids_suffix) VALUES ('acf30bc858021abdeee66a42b9d60df0fec07ee1522e3de2fde29c9c635a4a5f', 'MR T2', 'protocol2', 'yes', 'None', '01-07-2019', 'sub-04ST71MDDDD/ses-Pre/anat/sub-04ST71MDDDD_ses-Pre_acq-acq_Reference-T2star_T2star_sidecar.json', '04ST71MDDDD', 'Pre', 'nii.gz', 'NifTI', 'acq', 'T2star');