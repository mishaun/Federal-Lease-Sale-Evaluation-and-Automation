import os
import pandas as pd
from settings.etl_config import sales_path

def load_parent_table_sales(sqlalch_engine):
    '''

    :param sqlalch_engine: connection string for sql alchemy
    :return: function will create and update the parent table in the database, which will be the sales info table
    all other tables will need a sale id to correctly reference the data in the child tables
    '''

    # getting list of sale folders to iterate through
    salefolders = list(filter(lambda x: ".DS" not in x, os.listdir(sales_path)))
    salefolders

    ## Building sale information table
    # extracting date from sale name
    import re
    saledates = list(map(lambda x: re.findall("\d*-\d*-\d*", x)[0], salefolders))

    #creating dateframe of sale name and sale date
    saleinfoDF = pd.DataFrame()
    saleinfoDF['sale_name'] = salefolders
    saleinfoDF['sale_date'] = saledates
    #covnerting sale date from string to datetime object
    saleinfoDF['sale_date'] = pd.to_datetime(saleinfoDF['sale_date'])


    try:
        saleinfoDF.to_sql('sale_info', sqlalch_engine, if_exists='append', index=False)
    except Exception as e:
        print(e)


if __name__ == '__main__':

    #testing loading parent table function
    from etl.build_db_connection import build_db_connection
    engine = build_db_connection(sqlalch=True)

    load_parent_table_sales(engine)