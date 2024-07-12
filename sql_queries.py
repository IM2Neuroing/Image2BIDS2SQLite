'''
Functions to run sqlite queries to fetch, insert and update data in database
'''
import os
import sqlite3
import logging

#TO DO: remove these paths, will be passed to function as variables
db_data_root = '/DATA_RAID5/ParametersPrediction/stIM2Slicer_inputDir/'
db_path = os.path.join(db_data_root, 'db_stIM2Slicer.db')
db_path_new = '/DATA_RAID5/ParametersPrediction/im2neuro-stimulationparamsoptim_ma-eli/stIM2Analysis/New_database/DBS_database.db'
bids_path = '/DATA_RAID5/SNF-Parameters-Prediction/' #SNF-Parameters-Prediciton corresponds to the bids folder "project"

'''
The function retrieves a list of all tables in the database. Iterates through each table and fetches information about 
its columns. Constructs a dictionary (tables_dict) where each entry represents a table, 
with the table name as the key and a list of its column names as the value.
Args:
database_path: a string representing the file path to the SQLite database
Returns: 
a dictionary where keys are table names, and values are lists containing the column names associated with each table in the SQLite database
'''
def get_db_dict(database_path):

    sqliteConnection = None
    try:
        #open connection with db
        sqliteConnection = sqlite3.connect(database_path)
        cursor = sqliteConnection.cursor()
    except sqlite3.Error as error:
        logging.error("Failed to connect to db", error)

    # Dictionary to store table names and their columns
    tables_dict = {}

    try:
        # Get a list of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Iterate through each table
        for table in tables:
            table_name = table[0]
            columns = []

            # Get information about each column in the table
            cursor.execute(f"PRAGMA table_info({table_name});")
            column_info = cursor.fetchall()

            # Extract column names
            for col in column_info:
                columns.append(col[1])

            # Add the table and its columns to the dictionary
            tables_dict[table_name] = columns

    except sqlite3.Error as e:
        print("Error:", e)

    finally:
        # Close the database connection
        sqliteConnection.close()
    
    return tables_dict

'''
The function generates the statement needed to join tables which can be used in the get_db_row function afterwards
Args:
tables: array with tables names
attributes: array with tables attributes used for the join. The order of the attributes should follow the order of tables
join_type: string indicating the type of join (INNER, OUTER, LEFT, RIGHT)
Returns:
join_statement: string with SQL statement to join tables, to be used in the SELECT queries
'''
def gen_join_statement(tables, attributes, join_type):
    join_statement = ''
    for i in range(len(tables)-1):
        join_statement = join_statement + join_type + ' JOIN ' + tables[i+1] + ' ON ' +\
            tables[i] + '.' + attributes[i] + ' = ' + tables[i+1] + '.' + attributes[i+1] + ' '
    join_statement = tables[0] + ' ' + join_statement
    return join_statement

'''
The function constructs a SELECT query with conditions based on the provided column names and values.
Args: 
table_name: A string representing the name of the table in the SQLite database to check.
values: A dictionary where keys are column names, and values are the corresponding values to check for in the row.
database_path: A string representing the file path to the SQLite database. It should include the filename and extension.
attribute: A string with the name of the searched attribute. If entire row is desired attribute = *
equal: bool variable. If True the WHERE condition is an equivalence, otherwise it's a difference
Returns:
result + True: if row exists and has been successfully selected
'NA' + False: if row doesn't exist
'error' + False: if there was an error
'''
def get_db_row(table_name, values, database_path, attribute, equal):
    
    if equal is True:
        sign = '='
    else:
        sign = '!='
    
    # Connect to the SQLite database
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    try:
        # Build the SELECT query
        query = f"SELECT {attribute} FROM {table_name} WHERE "
        conditions = [str(col) + ' ' + sign + ' ?' for col in values.keys()]
        query += " AND ".join(conditions)
        # Execute the query
        cursor.execute(query, tuple(values.values()))

        # Fetch the result(s)
        result = cursor.fetchall()

        # Check if a row exists
        if result:
            return result, True
        else:
            return [('NA',)], False

    except sqlite3.Error as e:
        print("Error:", e)
        return 'error', False

    finally:
        # Close the database connection
        connection.close()


'''
The function updates a SQL database row using the UPDATE statement
Args:
table_name: string with name of table to update
values: dictionary with column names and corresponding values to insert
database_path: string representing the file path to the SQLite database. It should include the filename and extension.
condition: dictionary with the condition indicating which row(s) should be updated
'''
def update_row(table_name, values, database_path, condition):
    
    # Connect to the SQLite database
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    try:
        # Build the UPDATE query
        query = f"UPDATE {table_name} SET "
        set_clause = [f"{col} = ?" for col in values.keys()]
        query += ", ".join(set_clause)
        where_clause = " AND ".join([f"{key} = ?" for key in condition.keys()])
        query += f" WHERE {where_clause};"
        cursor.execute(query, tuple(values.values()) + tuple(condition.values())) 
        connection.commit()
    except sqlite3.Error as e:
        print("Error:", e)
    finally:
        # Close the database connection
        connection.close()

'''
The function retrieves the names of primary key columns for a specified SQLite table
Args:
table_name: A string representing the name of the SQLite table for which to obtain primary key information.
database_path: A string representing the file path to the SQLite database. It should include the filename and extension.
Returns:
primary_keys: A list containing the names of columns that are marked as primary keys for the specified table. 
If there are multiple primary keys (composite primary key), the list will contain multiple column names. If no primary keys are found, the function returns an empty list. If there is an error during the process, the function returns None.
'''
def get_primary_keys(table_name, database_path):
    # Connect to the SQLite database
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    try:
        # Query the sqlite_master table to get information about the table
        cursor.execute(f"PRAGMA table_info({table_name});")
        table_info = cursor.fetchall()
        # Find columns that have the 'pk' flag (primary key)
        primary_keys = [column[1] for column in table_info if column[5]]

        return primary_keys

    except sqlite3.Error as e:
        print("Error:", e)
        return None
    finally:
        # Close the database connection
        connection.close()



'''
The function  inserts a new row into an SQLite table if a row with the same primary key values does not already exist. 
If a matching row is found, it updates the existing row with new values.
Args:
table_name: A string representing the name of the SQLite table where the data is to be inserted or updated.
data: A dictionary containing column names and corresponding values for the row to be inserted or updated.
database_path: A string representing the file path to the SQLite database. It should include the filename and extension.
Returns:
None
'''
def insert_or_update(table_name, data, database_path):
    # Get table primary key columns
    pk = get_primary_keys(table_name, database_path)
    # Retain the values of primary key columns from the data dictionary
    data_pk_only = {key: value for key, value in data.items() if key in pk}
    data_no_pk = {key: value for key, value in data.items() if key not in pk}
    # Check if row already exists in database - check only the primary key columns
    row, exists = get_db_row(table_name, data_pk_only, database_path, '*', True) 
    
    try:
       # Connect to the SQLite database
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor() 
        # Get column names
        columns = ', '.join(data.keys())
        # Get tuple with column values to insert
        values = ', '.join(['"' + str(value) + '"' for value in data.values()])
        # If row doesn't exist use insert query to add it, otherwise update the row
        if exists is False:
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            cursor.execute(query)
        else:
            query = f"UPDATE {table_name} SET "
            set_clause = [f"{col} = ?" for col in data_no_pk.keys()]
            query += ", ".join(set_clause)
            where_clause = " AND ".join([f"{key} = ?" for key in data_pk_only.keys()])
            query += f" WHERE {where_clause};"
            cursor.execute(query, tuple(data_no_pk.values()) + tuple(data_pk_only.values()))   
        connection.commit()
    except sqlite3.Error as e:
        print("Error:", e)
    finally:
        # Close the database connection
        connection.close()

'''
The function runs a query to select the maximum value from a table column in a database.
Args:
table_name: A string with name of table to check
column: A string with name of column
database_path: A string representing the file path to the SQLite database. It should include the filename and extension.
Returns:
max: maximum value extracted from table
'''
def get_max_from_table(table_name, column, database_path):
    try:
       # Connect to the SQLite database
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor() 
        query = 'SELECT MAX(' + column + ') FROM ' +table_name
        cursor.execute(query)
        max = cursor.fetchone()
        if max[0] is None:
            return 0
        else:
            return max[0]
    except sqlite3.Error as e:
        print("Error:", e)
    finally:
        # Close the database connection
        connection.close()


'''
The function extracts information about the file contained in the file name which follows the BIDS naming standard. If some information is not found,
the corresponding parameter is set to NA.
Args:
file_name: string containing the file name. For example: sub-<subject>_space-<VERSION>_ses-<Pre|Post>_acq-<ppp>_A2P_warp.nii.gz 
is_label: bool value indicating whether the file is a label
Returns:
subject: string with subject alphanumeric identification code (e.g. <subject>)
session: string with information about the session in which the file was acquired (e.g. <Pre|Post>)
acquisition: string with information about the image acquisition (e.g. <ppp>)
suffix: last word before file extension, gives information on the type of file we have (e.g. warp)
extension: file extension (e.g. nii.gz)
hemisphere (applicable only to labels): R or L 
structure (applicable only to labels): name of structure that the label identifies
'''
def get_bids_info(file_name, is_label):
    bids_info = file_name.split('_')
    subject = session = acquisition = suffix = extension = hemisphere = structure = 'NA'
    # Loop through bids_info elements except the last one (which we know it contains the suffix+file extension)
    for i in range(len(bids_info)-1):
        if 'sub' in bids_info[i]:
            subject = bids_info[i].split('-')[1]
        elif 'ses' in bids_info[i]:
            session = bids_info[i].split('-')[1]
        elif 'acq' in bids_info[i]:
            acquisition = bids_info[i].split('-')[1]
    # Get file suffix and extension
    suffix = bids_info[-1].split('.', 1)[0]
    extension = bids_info[-1].split('.', 1)[1]
    # If file is a label get hemisphere and structure from file name
    if is_label:
        hemisphere = bids_info[-2].split('-', 1)[0]
        structure = bids_info[-2].split('-', 1)[1]
    else:
        pass

    return subject, session, acquisition, suffix, extension, hemisphere, structure

'''
The function saves files information from the BIDS folder structure to respective tables in db. The file information is saved in the tables 'bids' and 'files' 
and also 'labels' if the file represents a label (understandable from the prefix _label in the file name). 
The string 'sub-' in the file name identifies the files which should be saved in the db. Moreover the .json files are not considered by the function since they are part of the main file
attributes (according to BIDS rules). The function extracts the file attributes which can be obtained from the file name (standardized according to
BIDS standard) and stores them as attirbutes in the database tables.
Warning: before running this function the table 'subject' should be populated to allow the retrieval of the subject_id, otherwise it will be inserted as 'NA'  
Args: 
bids_path: path to project folder containing atlas and patients files organised according to bids standard.
database_path: A string representing the file path to the SQLite database. It should include the filename and extension.
Return:
files_loaded: bool variable, if True indicates that the for loop has run until the end
counter: int variable indicating the number of files saved in database
'''
def bids_to_db(bids_path, database_path):
    bids_table = 'bids'
    label_table = 'labels'
    file_table = 'files'
    # Initialize counter to keep track of number of added files
    counter = 0
    # Initialize flag indicating end of for loop 
    files_loaded = False
    # List folders and files contained in the bids project folder
    for root, dirs, files in os.walk(bids_path):
        # Loop through files and if they contain the string 'sub' save them in db
        # Differentiate between labels and other files. The labels should be saved in the 'labels' table
        for file in files:
            # Check that file name is not an empty string
            if file:
                # Save in db only files containing the string 'sub' and not belonging to the Electrodes folder
                if 'sub-' in file and 'Electrodes' not in os.path.join(root, file):
                    # The .json files are saved in the 'relative_sidecar_path' of the 'bids' table. The .seg.nrrd label path is saved in 'relative_seg_path' in table 'labels'
                    if '.json' or '.seg.nrrd' not in file:
                        # Check the file's suffix to know whether it should be saved also in the table 'labels' 
                        if '_label' in file:
                            is_label = True
                            # Create segmented label file name, and save into variable if it exists
                            label_seg_file = file.split('.', 1)[0] + '.seg.nrrd'
                            abs_seg_path = os.path.join(root, label_seg_file)
                            if os.path.exists(abs_seg_path):
                                rel_seg_path = abs_seg_path.replace(bids_path, '/')
                            else:
                                rel_seg_path = 'NA'
                        else:
                            is_label = False
                            rel_seg_path = 'NA'
                        # Get bids information from the file name
                        subject, session, acquisition, suffix, extension, hemisphere, structure = get_bids_info(file, is_label)
                        # Get file relative path
                        rel_file_path = os.path.join(root, file)
                        rel_file_path = rel_file_path.replace(bids_path, '/')
                        # Get relative sidecar path, if the .json file exists, otherwise set it to NA
                        sidecar_file = file.split('.', 1)[0] + '.json'
                        abs_sidecar_path = os.path.join(root, sidecar_file)
                        if os.path.exists(abs_sidecar_path):
                            rel_sidecar_path = abs_sidecar_path.replace(bids_path, '/')
                        else:
                            rel_sidecar_path = 'NA'
                        # Get subject_id from the table subject # TODO:string manipulation since patient_id_acr may contain some special characters
                        subject_dict = {'patient_id_acr': subject}
                        subject_id, subj_exists = get_db_row('subject', subject_dict, database_path, 'subject_id', True)
                        # Extract subject id, since it is returned in format [(subj_id,)]
                        subject_id = subject_id[0][0]
                        # Get maximum bids_image_info_id assigned until now to compute the one for the new row (max+1)
                        bids_index = int(get_max_from_table(bids_table, 'bids_image_info_id', database_path)) + 1
                        # Do the same for the table files and labels
                        label_column = label_table.replace('s','') + '_id' #e.g. index_column = label_id
                        label_index = int(get_max_from_table(label_table, label_column, database_path)) + 1
                        file_column = file_table.replace('s','') + '_id' #e.g. index_column = label_id
                        file_index = int(get_max_from_table(file_table, file_column, database_path)) + 1
                        # Get the file_type attribute from the relative file path. For the derivatives it's the name of the derivative sub-folder.
                        # The other files are divided between atlas and raw patient images
                        if 'derivatives' in rel_file_path:
                            file_type = rel_file_path.split('/')[1] 
                        elif 'ATLAS' in file:
                            file_type = 'Atlas'
                        else:
                            file_type = 'Raw image'
                        # Insert row in 'bids' table
                        db_dict = get_db_dict(database_path)
                        columns_bids = db_dict.get(bids_table)
                        data_bids = [bids_index, 'NA', 'NA', 'NA', 'NA', 'NA', rel_file_path, rel_sidecar_path, subject, session, extension, 'NA', acquisition, suffix]
                        insert_or_update(bids_table, dict(zip(columns_bids,data_bids)), database_path)
                        # Insert row in either both 'labels' and 'files' table or only 'files'
                        if is_label:
                            data_label = [label_index, bids_index, hemisphere, structure, 'NA', 'NA', 'NA', 'NA', rel_seg_path]
                            columns_label = db_dict.get(label_table)
                            insert_or_update(label_table, dict(zip(columns_label,data_label)), database_path)
                        else:
                            pass
                        data_files = [file_index, subject_id, bids_index, file_type, 'NA', 'NA']
                        columns_files = db_dict.get(file_table)
                        insert_or_update(file_table, dict(zip(columns_files,data_files)), database_path)
                        # Increment file counter
                        counter = counter + 1
                    else: 
                        pass
                else:
                    pass
    
    files_loaded = True
    return files_loaded, counter