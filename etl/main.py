
#import modules
from etl.build_db_connection import build_db_connection
from etl.etl_functions import *
from load_parent_table import load_parent_table_sales
from settings.etl_config import sales_to_run, replaceExistingRecords, mappings

def main():
    #setting up db conections
    db_connection = build_db_connection(pymy = True)
    engine = build_db_connection(sqlalch=True)
    #########

    #load parent table
    load_parent_table_sales(engine)


    # getting list of sale folders to run from config file
    for sale in sales_to_run:
        print(f'Migrating Records to Database for sale {sale}\n')

        # looping through mapping dictionary imported from config file to get path, parse information, and table and file names
        for data_category in mappings.keys():
            path = mappings[data_category]['path']
            parse = mappings[data_category]['parseCols']
            table_and_file = mappings[data_category]['table_names_file_names']

            print(f"Extracting data category: {data_category}")

            for table, file in table_and_file.items():


                df = read_file(sale_name=sale, datadir = path, file_keyword=file, parseDict=parse)
                saleid = get_saleID(sale, db_connection)
                df = add_foreignKey_to_df(df, 'sale_id', saleid)

                print(f'Migrating records for table {table} pertaining to sale {sale}]')
                is_exists = check_if_records_exist(table_name=table, sale_id=saleid, db_conn=db_connection)
                load_or_replace_to_table(df=df, table_name=table, sale_id = saleid, pymy_db_conn=db_connection, sqlaclch_engine=engine, recordsExist=is_exists, IsReplace=replaceExistingRecords)

    db_connection.close()


if __name__ == '__main__':
    main()






