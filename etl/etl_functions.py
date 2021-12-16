import os
import pandas as pd
import pymysql.err


def read_file(sale_name, datadir, file_keyword, parseDict = None):
    '''

    :param sale_name: name of sale folder to access
    :param datadir: top directory for data files
    :param file_keyword: key word to search directory list to pull file name (data folders do not have subfolders identifying file names)
    :return: dataframe, df, of desired file
    '''

    # file path for data files to be loaded
    datafolderpath = f'../Sales/{sale_name}/{datadir}/'

    # list of files in data directory to be loaded
    fileoptions = os.listdir(datafolderpath)

    try:
        # searching for file name and storing it as filename
        filename = list(filter(lambda x: file_keyword.lower() in x.lower(), fileoptions))[0]
        filepath = datafolderpath+filename
    except:
        raise KeyError('file keyword passed did not recognize file in passed directory')

    #if parseeDict is passed, then use values to parse dataframe
    if type(parseDict) != type(None):
        headerRow = parseDict['header']
        use_cols = parseDict['usecols']
        df = pd.read_excel(filepath, header = headerRow, usecols= use_cols)
    else:
        df = pd.read_excel(filepath)
    return df


def get_saleID(sale, engine):

    '''

    :param sale: sale name to be passed to find sale id in parent table
    :param db_conn: sql alchemy connection/engine object
    :return: sale id number
    '''

    sql = f'''
    SELECT id 
    FROM sale_info
    WHERE sale_name = '{sale}';
    '''

    sale = pd.read_sql(sql,con = engine)
    id = sale.iloc[0].values[0]

    return id

def add_foreignKey_to_df(df, fk_name, foreign_key):
    '''

    :param df: df to be loaded as a child table to database
    :param fk_name: foreign key name to be given to df
    :param foreign_key: foreign key value to be passed
    :return: df with foreign key added
    '''
    df[fk_name] = foreign_key
    return df


def check_if_records_exist(table_name, sale_id, db_conn):

    '''
    :param table_name: table name to be created or inserted into in database
    :param sale_id: sale id from parent table to check if records exist for particular sale in insert table
    :param db_conn: pymysql connection string for running queries
    :return: check if records exist for records exists based on its associated sale id and table name
    '''

    #instantiating a cursor object
    cursor = db_conn.cursor()

    #sql query to check if records with sale id exist in specified table
    sql =  f''' 
    SELECT COUNT(1) from {table_name}
    WHERE sale_id = {sale_id}
    '''

    #try statement needed to ensure code exeuctes upon building new table
    #sql query to find sale id fails when table has not been created in the database
    try:
        cursor.execute(sql)
        records = cursor.fetchone()

        #if records are found, print true
        if records[0] > 0:
            print("Previous Records are found for this sale.")
            return True
        else:
            return False

    except Exception as e:
        print(e)
        print("No previous records or table found.")
        return False


def load_or_replace_to_table(df, table_name, sale_id, pymy_db_conn, sqlaclch_engine, recordsExist, IsReplace = True):

    '''

    :param df: dataframe to be staged for inserting into database
    :param IsReplace: read from config file or passed in to delete exisitng records if found in table for replacement.
                        Defaulted to True to ensure no duplicate sets of data are inserted.
    :param recordsExist: boolean value passed in, if false then insert table and break out of function. else proceed
    :param table_name: table name to be created or inserted into in database
    :param sale_id: sale id from parent table to check if records exist for particular sale in insert table
    :param db_conn: pymysql connection string for running queries
    :return: Boolean to flow program - if program has records existing, will return false to skip insert statement unless
            IsReplace flag is set to true, then records will be deleted and boolean will return True to insert records
    '''

    #if records are absent, load in the table
    if recordsExist == False:
        try:
            df.to_sql(table_name, con=sqlaclch_engine, if_exists='append', index=False)
            return print("Records inserted to table")
        except Exception as e:
            print(e)
            # if schema changed from source data, filter columns from source data to the ones found in the database
            columnsindb = pd.read_sql(f"select * from {table_name} limit 0", sqlaclch_engine).columns
            df[columnsindb].to_sql(table_name, con=sqlaclch_engine, if_exists='append', index=False)

    # if records are already present, check replace parameter to delete existing records and insert
    if IsReplace:

        cursor = pymy_db_conn.cursor()

        #delet statement to remove records based on sale id within specified table
        del_sql = f'''
        DELETE FROM {table_name}
        WHERE sale_id = {sale_id};
        '''
        print('Deleting existing rows. Records will be replaced sqlalchemy and pandas insert ')
        cursor.execute(del_sql)
        pymy_db_conn.commit()
        cursor.close()

        try:
            #after delete query, close connection and insert to table
            df.to_sql(table_name, con=sqlaclch_engine, if_exists='append', index=False)
        except Exception as e:
            print(e)
            #if schema changed from source data, filter columns from source data to the ones found in the database
            columnsindb = pd.read_sql(f"select * from {table_name} limit 0", sqlaclch_engine).columns
            df[columnsindb].to_sql(table_name, con=sqlaclch_engine, if_exists='append', index=False)

    else:
        print("Records are found for this sale. Not deleting and will not replace")


if __name__ == "__main__":
    print('Running Read Python Script and Testing Functions')

    from settings.etl_config import *

    # Testing Read File Function
    testSale = sales_to_run[0]
    testdatadir = mappings['output_data']['path']
    testTable = list(mappings['output_data']['table_names_file_names'].keys())[0]
    testFile = mappings['output_data']['table_names_file_names'][testTable]

    read_file(testSale, testdatadir, testFile)

    #########################################

    # Testing Get Sale ID function
    from etl.build_db_connection import build_db_connection

    db_connection = build_db_connection(pymy = True)
    engine = build_db_connection(sqlalch=True)

    get_saleID(testSale, engine=engine)

    #########################################

    # Testing check if exists function
    df = read_file(testSale, testdatadir, testFile)
    sale_id = get_saleID(testSale, engine= engine)

    df = add_foreignKey_to_df(df, 'sale_id', sale_id)

    engine = build_db_connection(sqlalch=True)
    recordsExist = check_if_records_exist(testTable, sale_id, db_connection)

    # load_or_replace_to_table(df, table_name=testTable, sale_id=sale_id, pymy_db_conn=db_connection, sqlaclch_engine=engine, recordsExist=recordsExist, IsReplace=True)

    db_connection.close()

    #### Testing Read File to pull sale note template

    salenotes_dir = "Sale Template Automation"
    sale_note_parse = {'header': 6, "usecols": 'B:U'}

    salenotesDF = read_file(testSale, salenotes_dir, 'Sale Notes.xlsm', parseDict=sale_note_parse)

    #### Testing Read File to pull automated sale notes

    automate_salenotes_dir = "Results"
    auto_notesDF = read_file(testSale, automate_salenotes_dir, 'Auto')