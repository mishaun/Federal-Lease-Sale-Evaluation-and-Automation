import os
import configparser
import pandas as pd
import pymysql

# establish config reader to get data base credentials
config = configparser.ConfigParser()
config.read('../settings/dbconfig.ini')

db_config = dict(config.items('DATABASE'))

# creating connection string using sqlalchemy module
from sqlalchemy import create_engine
engine = create_engine(f'mysql+pymysql://{db_config["user"]}:{db_config["pass"]}@{db_config["host"]}/{db_config["database"]}')

# getting list of sale folders to iterate through
salefolders = list(filter(lambda x: ".DS" not in x, os.listdir('../Sales/')))
salefolders



## Building sale information table
#extracting date from sale name
import re
saledates = list(map(lambda x: re.findall( "\d*-\d*-\d*", x)[0], salefolders))

saleinfoDF = pd.DataFrame()
saleinfoDF['sale_name'] = salefolders
saleinfoDF['sale_date'] = saledates
saleinfoDF['sale_date'] = pd.to_datetime(saleinfoDF['sale_date'])
saleinfoDF.head()

try:
    saleinfoDF.to_sql('sale_info', engine, if_exists='append', index=False)
except Exception as e:
    print(e)


# loop to pull all data from sales
for folder in salefolders:
    print(folder)


def read_file(sale_name, datadir, file_keyword):
    '''

    :param sale_name: name of sale folder to access
    :param datadir: top directory for data files
    :param file_keyword: key word to search directory list to pull file name (data folders do not have subfolders identifying file names)
    :return: dataframe, df, of desired file
    '''

    datafolderpath = f'../Sales/{sale_name}/{datadir}/'

    fileoptions = os.listdir(datafolderpath)

    try:
        filename = list(filter(lambda x: file_keyword.lower() in x.lower(), fileoptions))[0]
        filepath = datafolderpath+filename
    except:
        raise KeyError('file keyword passed did not recognize file in passed directory')

    df = pd.read_excel(filepath)
    return df


def get_saleID(sale, db_conn):

    sql = f'''
    SELECT id 
    FROM sale_info
    WHERE sale_name = '{sale}';
    '''

    sale = pd.read_sql(sql,con = db_conn)
    id = sale.iloc[0].values[0]

    return id

def check_if_records_exist_and_delete(df, table_name, sale_id, db_conn):

    cursor = db_conn.cursor()

    sql =  f''' 
    SELECT COUNT(1) from {table_name}
    WHERE sale_id = {sale_id}
    '''
    try:
        cursor.execute(sql)
        records = cursor.fetchone()

        if records[0] > 0:
            print('records of this sale already exits. Deleting existing rows.  Records will be replaced sqlalchemy and pandas insert ')

            del_sql = f'''
            DELETE FROM {table_name}
            WHERE sale_id = {sale_id};
            '''
            cursor.execute(del_sql)

    except Exception as e:
        print(e)
        print("No previous records or table found. New records will be appended to newly created table")

    db_conn.commit()
    cursor.close()


if __name__ == '__main__':

    #setting up db conection
    db_connection = pymysql.connect(user= db_config["user"], password = db_config["pass"], host = db_config["host"], database=db_config["database"])
    cursor = db_connection.cursor()

    #test query
    cursor.execute('show tables;')
    print(cursor.fetchall()[0])

    #########

    #testing function read_dir
    testSale = "BLM MT 9-22-20"
    testdataDir = "Output Data/Sale Tracts Activity Data"
    file_like = "Lease"

    df = read_file(testSale, testdataDir, file_like)
    df.head()

    #testing when no file is recognized
    # read_file(testSale, testdataDir, "testingnofilelikeness")

    print(read_file(testSale, 'Sale Template Automation', 'Sale Notes.xlsm'))

    ########

    #testing get sale id
    get_saleID(testSale, engine)

    from settings.datamap_config import table_names_file_names

    table_names_file_names['leases']

    # keywords_maptotable = ['leases']
    # # keywords_maptotable = ['leases', 'permits', 'oldprod', 'newprod']
    #
    # for word in keywords_maptotable:
    #     df = read_file(testSale, testdataDir, word)
    #
    #     df['sale_id'] = get_saleID(testSale, engine)
    #
    #     df.to_sql(word, con=engine, if_exists='append', index=False)
    #
    #     print(df.head())


    # testing if exists function
    check_if_records_exist_and_delete(df, 'leases', 1, db_connection)

for sale in salefolders:
    for table, file in table_names_file_names.items():

        print(f'Migrating Records to Database for sale {sale}')
        df = read_file(sale_name =sale, datadir = "Output Data/Sale Tracts Activity Data", file_keyword=file)
        sale_id = get_saleID(sale, db_connection)
        df['sale_id'] = sale_id

        print(f'Migrating records for table {table}')
        check_if_records_exist_and_delete(df=df, table_name=table, sale_id=sale_id, db_conn=db_connection)
        df.to_sql(table, con=engine, if_exists='append', index=False)

