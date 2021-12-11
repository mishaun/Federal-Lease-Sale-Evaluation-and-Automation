# ## Goals of Project
#
# 1. Automate the process of writing notes in a natural language format of each tract in a BLM Oil and Gas Lease Sale
# 2.  Create visualizaitons tract by tract for CEO depicting permitting, new production, and leasing activity within a given radius
# 3.  Create a predictive model to estimate the purchase price based on historical activity, production, permits, and commodity prices

import configparser
import os
config = configparser.ConfigParser()
# config_path = 'app/settings/config.ini'
config_path = '../settings/config.ini'
config.read(config_path)

#changing working directory to sale in config file±
os.chdir(f'../Sales/{config.get("SALE", "sale_dir")}')
print(os.getcwd())

#using from import * to get variables in program memory since functions use global variable names
from app.clean_prep import *
from app.wrangle_filter import *

if __name__ == '__main__':
    prepareTractFilter(1)
    wrangle_and_export(tractshp)

    print('running main')


