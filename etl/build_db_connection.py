import configparser
import pymysql
from settings.etl_config import db_config_path


def build_db_connection(pymy = False, sqlalch = False):
    '''
    :param pymy: Boolean value - if true, then return pymysql connectin object 
    :param sqlalch: if true, then return connection string used for sqlalchemy
    :return: return pymysql db connection or sqlalchemy engine/connection string
    '''
    config = configparser.ConfigParser()
    config.read(db_config_path)
    db_config = dict(config.items('DATABASE'))

    if sqlalch:
        from sqlalchemy import create_engine
        engine = create_engine(f'mysql+pymysql://{db_config["user"]}:{db_config["pass"]}@{db_config["host"]}/{db_config["database"]}')
        return engine

    if pymy:
        # setting up db conection
        db_connection = pymysql.connect(user=db_config["user"], password=db_config["pass"], host=db_config["host"], database=db_config["database"])
        return db_connection
    
    if pymy == False and sqlalch == False:
        raise KeyError('Either pymy or sqlalch must be true to return db connection string')

if __name__ == '__main__':


    #testing build connection string
    print('building db connection')
    
    db_conn = build_db_connection(pymy = True)
    cursor = db_conn.cursor()
    cursor.execute('show tables;')
    results = cursor.fetchall()
    
    for result in results:
        print(result[0])

    cursor.close()
    db_conn.close()

    engine = build_db_connection(sqlalch=True)