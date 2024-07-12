import sqlite3
import re
import os
import pandas as pd
import logging

# Configure logger
workflow_logger = logging.getLogger('workflow_logger')

def create_database(database_name, database_sql ,wipe=False):
    """
    This function creates a new SQLite database using the provided SQL schema.

    Args:
    database_name (str): The name of the database.
    database_sql (str): The path to the SQL schema file.
    wipe (bool): A flag to indicate if the database should be wiped if it already exists.

    Returns:
    None
    """

    # First check if the database already exists
    if os.path.exists(database_name):
        if wipe:
            wipe_sqlite_database(database_name)
            workflow_logger.info("Database wiped: %s", database_name)
        # If the database already exists, return
        else:
            workflow_logger.info("Database have not been wiped: %s", database_name)
            return None
        
    try:
        # Create a connection to the database
        conn = sqlite3.connect(database_name)

        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Open the SQL script file and read the content
        with open(database_sql, 'r') as sql_file:
            script = sql_file.read()
        workflow_logger.debug("Database schema loaded")

        # Execute the SQL script to initialize the database
        cursor.executescript(script)
        conn.commit()
        workflow_logger.info("Database created: %s", database_name)

    except sqlite3.Error as e:
        workflow_logger.error("Database Creation: An error occurred: SQL-shema", e)
        return None
    
    finally:
        # Close the database connection
        conn.close()


def wipe_sqlite_database(db_name):
    """
    This function wipes all tables in a SQLite database.

    Args:
    db_name (str): The name of the SQLite database.

    Returns:
    None
    """

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
        tables = cursor.fetchall()
        
        # Drop all tables
        for table_name in tables:
            cursor.execute(f"DROP TABLE {table_name[0]};")
            workflow_logger.debug(f"Table {table_name[0]} dropped")

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        workflow_logger.debug("Database wiped: %s", db_name)

    except sqlite3.Error as e:
        workflow_logger.error("Database Creation (Wiping-step): An error occurred:", e)
        return None

    finally:
        # Close the database connection
        conn.close()

def execute_sql_statement(sql_statement, db_file):
    """
    :param db_file: complete file path to db
    :param sql_statement: sql statement to select, insert, update or delete row
    :return: None or the result of the query
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # Execute the SQL statement
        cursor.execute(sql_statement)

        # If the statement is a query, fetch all rows
        if sql_statement.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            return rows

        # If the statement is an update, delete, or insert, commit the changes
        else:
            conn.commit()
            workflow_logger.debug(f"Statement:{sql_statement}: ran successfully")
            return "Statement executed successfully."

    except sqlite3.Error as e:
        workflow_logger.error(f"Statement:{sql_statement}: failed: {e}")
        return f"Statement:{sql_statement}: failed: {e}"

    finally:
        # Close the database connection
        cursor.close()
        conn.close()

def execute_sql_script(sql_script, db_file):
    """
    This function executes an SQL script on a SQLite database.

    Args:
    sql_script (str): The SQL script to be executed.
    db_file (str): The path to the SQLite database.

    Returns:
    None
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # Execute the SQL script
        cursor.executescript(sql_script)
        conn.commit()
        return "successfully."

    except sqlite3.Error as e:
        workflow_logger.exception("SQL script execution failed:", e)
        return e

    finally:
        # Close the database connection
        cursor.close()
        conn.close()

# Data check Function
def data_check(db_file):
    """
    Function to check if the data was loaded into the database.
    It retrieves the number of rows in each table and logs the result.
    :param db_file: complete file path to db
    :return: None
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    
    # Create a cursor object
    cursor = conn.cursor()
    
    # Execute the SQL query to retrieve all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    
    # Fetch the result of the query
    tables = cursor.fetchall()
    
    # For each table, execute a SQL query to count the number of rows
    for table in tables:
      cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
      count = cursor.fetchone()[0]
      workflow_logger.info(f"Data check: Table {table[0]} has {count} rows.")
    
    # Close the connection to the database
    conn.close()

def fix_sql_query(sql_query):
    """
    Fix some errors that occur from automatically constructing the query strings
    1) convert f" 'None'  " to f" None  " otherwise the value is not added as None-type to the db but as 'None'-string
    2)
    :param sql_query:
    :return: fixed_query:
    """

    # Use regular expressions to replace 'NULL' with 'IS NULL' while preserving single quotes
    fixed_query = re.sub(r"= 'NULL'", "IS NULL", sql_query)
    return fixed_query

def get_db_dict(db_path):
    """
    The function retrieves a list of all tables in the database. Iterates through each table and fetches information about 
    its columns. Builds a dictionary (tables_dict) where each entry represents a table, with the table name as the key and a list of its column names as the value.
    
    Args:
    db_path (str): the absolute file path to the SQLite database

    Returns: 
    tables_dict (dict): a dictionary where keys are table names, and values are lists containing the column names associated with each table in the SQLite database
    """

    # Dictionary to store table names and their columns
    tables_dict = {}
    # Generate statement 
    select_statement = f"SELECT name FROM sqlite_master WHERE type='table';"
    # Get list of tables from db
    tables = execute_sql_statement(select_statement, db_path)

    if (tables != []):

        # Iterate through tables
        for table in tables:
            table_name = table[0]
            columns = []

            # Get information about each column in the table
            query = f"PRAGMA table_info({table_name});"
            column_info = execute_sql_statement(query, db_path)

            # Extract column names
            for col in column_info:
                columns.append(col[1])

            # Add the table and its columns to the dictionary
            tables_dict[table_name] = columns

    return tables_dict

def gen_join_statement(tables, attributes, join_type):
    """
    The function generates the join statement between multiple tables

    Args:
    tables (list): list with tables names
    attributes (list): list with tables attributes used for the join. The order of the attributes should follow the order of tables
    join_type (str): string indicating the type of join (INNER, OUTER, LEFT, RIGHT)

    Returns:
    join_statement (str): string with SQL statement to join tables, to be used in the SELECT queries
    """

    join_statement = ''
    for i in range(len(tables)-1):
        join_statement = join_statement + join_type + ' JOIN ' + tables[i+1] + ' ON ' +\
            tables[i] + '.' + attributes[i] + ' = ' + tables[i+1] + '.' + attributes[i+1] + ' '
    join_statement = tables[0] + ' ' + join_statement
    
    return join_statement

def get_db_row(table_name, values, database_path, attribute, compare_signs):
    """
    The function builds a SELECT query with conditions based on the provided column names and values.
    
    Args: 
    table_name (str): a string representing the name of the table in the SQLite database to check.
    values (dict): a dictionary where keys are column names, and values are the corresponding values to check for in the row.
    database_path (str): absolute path to database
    attribute (str): a string with the name of the searched attribute. If entire row is desired attribute = *
    compare_signs (bool or list): bool variable or list of bool variables to indicate the sign (= or !=) to be used for each filter

    Returns:
    result + True: if row(s) exists and have been successfully selected
    'NA' + False: if row doesn't exist
    """
    
    sign_dict = {False:'!=', True:'='}

    if type(compare_signs) is list:
        # Get list of signs to build SELECT condition. e.g. [True, False, True] = [=, !=, =]
        sign_list = [sign_dict[key] for key in compare_signs]
    else: 
        # Create list of signs with the same sign repeated as many times as the number of attributes used to filter the table
        sign = sign_dict[compare_signs]
        sign_list = [sign]*len(values.keys())
    
    # Build the SELECT query
    conditions = []
    query = f"SELECT {attribute} FROM {table_name} WHERE "
    for i in range(len(sign_list)):
        key = list(values.keys())[i]
        string = str(key) + ' ' + sign_list[i] + ' ?' 
        conditions.append(string)
    query += " AND ".join(conditions)

    # Fetch the result(s)
    result = execute_sql_statement(query, database_path)

    # Check if a row exists
    if result:
        return result, True
    else:
        return [('NA',)], False
    
def get_primary_keys(table_name, database_path):
    """
    The function retrieves the names of primary key columns for a specified SQLite table
    
    Args:
    table_name (str): the name of the SQLite table for which to obtain primary key information.
    database_path (str): the absolute file path to the SQLite database
    
    Returns:
    primary_keys (list): A list containing the names of columns that are marked as primary keys for the specified table. 
    If there are multiple primary keys (composite primary key), the list will contain multiple column names. If no primary keys are found, the function returns an empty list. 
    """

    # Query the sqlite_master table to get information about the table
    query = f"PRAGMA table_info({table_name});"
    table_info = execute_sql_statement(query, database_path)
    # Find columns that have the 'pk' flag (primary key)
    primary_keys = [column[1] for column in table_info if column[5]]

    return primary_keys

def get_max_from_table(table_name, column, database_path):
    """
    The function runs a query to select the maximum value from a table column in a database.
    Can be used to get the highest value of the index column for example

    Args:
    table_name (str): name of table to check
    column (str): the name of the column
    database_path (str): absolute file path to the SQLite database

    Returns:
    max (int): maximum value extracted from table
    """
    
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

def insert_or_update(table_name, data, database_path, update=False):
    """
    The function  inserts a new row into an SQLite table if a row with the same primary key values does not already exist. 
    If a matching row is found, it updates the existing row with new values if the update flag is set to True.

    Args:
    table_name (str): name of the SQLite table where the data is to be inserted or updated.
    data (dict): dictionary containing column names and corresponding values for the row to be inserted or updated.
    database_path (str): absolute file path to the SQLite database
    update (bool): flag indicating whether to update an existing row or not. By default it's False
    """

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
            connection.commit()
            return "Statement executed successfully."
        elif ((exists is True) and (update is True)):
            query = f"UPDATE {table_name} SET "
            set_clause = [f"{col} = ?" for col in data_no_pk.keys()]
            query += ", ".join(set_clause)
            where_clause = " AND ".join([f"{key} = ?" for key in data_pk_only.keys()])
            query += f" WHERE {where_clause};"
            cursor.execute(query, tuple(data_no_pk.values()) + tuple(data_pk_only.values()))   
            connection.commit()
            return "Statement executed successfully."
        else:
            return "Entry already exists and will not be overwritten"
    
    
    except sqlite3.Error as e:
        workflow_logger.error(f"Insertion/update failed: {e}")
        return f"Insertion/update failed: {e}"
    finally:
        # Close the database connection
        connection.close()