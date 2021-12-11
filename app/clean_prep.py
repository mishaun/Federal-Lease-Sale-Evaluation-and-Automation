#!/usr/bin/env python
# coding: utf-8

# ## Goals of Project
# 
# 1. Automate the process of writing notes in a natural language format of each tract in a BLM Oil and Gas Lease Sale
# 
# 2.  Create visualizaitons tract by tract for CEO depicting permitting, new production, and leasing activity within a given radius
# 
# 3.  Create a predictive model to estimate the purchase price based on historical activity, production, permits, and commodity prices

# ## Goals of Module
# 
# 1.  Read in data necessary for sale note generation
# 2.  Clean dataframes by dropping uneeded features
# 3.  Convert date related columns to datetime.  
# 4.  Convert coordinate systems for geodata 


import pandas as pd
import geopandas as gp
import math
import os
#had to add GDAL_DATA variable to system variables and set value to the folder of gdal in C:\Users\mishaun\AppData\Local\Continuum\anaconda3\Library\share\gdal on my work computer
'GDAL_DATA' in os.environ


# # Reading in Data/Data Preparation for Automating Sale Notes
#dynamically storing sale shapefile by searching for WGS in filename
saleshapefile = list(filter(lambda x: 'WGS' in x.upper(), os.listdir('Data/')))[0]
shapezipfile = (f"zip://Data/{saleshapefile}")
tractshp = gp.read_file(shapezipfile, encoding = "utf-8")


#this is shapefile downloaded from drillinginfo holding well information
prodshp = gp.read_file("zip://Data/production.ZIP")
permitshp = gp.read_file("zip://Data/permits.ZIP")
oldprod = gp.read_file("zip://data/oldProduction.zip")

#reading in csv of leases - converting to a GeoDataFrame - initial coord system is epsg:4326
leases = pd.read_csv("Data/LeasesTable.CSV")
leasesgeo = gp.GeoDataFrame(leases, crs = {'init': 'epsg:4326'}, geometry=gp.points_from_xy(leases["Longitude (WGS84)"], leases["Latitude (WGS84)"]))


### Trimming and Cleaning Data

leasesgeo.drop(columns = ['Instrument Type', 'Instrument Date','Options/Extensions', 'DI Basin', 'Ext. Bonus',
       'Ext. Term (Months)', 'Abstract', 'Block', 'BLM', 'State Lease',
       'Grantee', 'Grantor Address', 'Grantee Address', 'Max Depth',
       'Majority Legal Assignee', 'DI Subplay', 'Min Depth',
       'Majority Assignment Effective Date','Majority Legal Assignee Interest','Majority Assignment Vol/Page'], inplace = True)

prodshp.drop(columns = ['LatestWtr','CumWtr',
       'Prior12Liq', 'Prior12Gas', 'LastTestDt', 'Prior12Wtr', 'LastFlwPrs',
       'LastWHSIP', '2moGOR', 'LatestGOR', 'CumGOR', 'Lst12Yield', '2moYield',
       'LatestYld', 'PeakGas', 'PkGasMoNo', 'PeakLiq', 'PkLiqMoNo', 'PeakBOE',
       'PkBOEMoNo', 'PkMMCFGE', 'PkMMCFGMoN', 'TopPerf', 'BtmPerf', 'GasGrav',
       'OilGrav','CompDate', 'GasGather',
       'LiqGather', 'LeaseNo'], inplace = True)

permitshp.drop(columns = ['OpReported', 'AmendDate', 'CntctName',
       'CntctPhone', 'OperAddrs', 'OperCity', 'OperState', 'OperZip',
       'OperCity30', 'Section', 'OperCity50', 'Township', 'Range', 'Block',
       'Survey', 'TVD_UOM', 'Abstract', 'WGID', 'H2S_Area','OFS_Reg', 'LeaseNo', 'PermDUOM',
       'PermitNo','OpCompany', 'OpTicker'], inplace=True)

oldprod.drop(columns= ['CumWtr', 'DISubplay', '1moLiq',
       '1moGas', '6moLiq', 'DIBasin', '6moGas', '6moBOE', '6moWater', 'DIPlay',
       'PracIP_Liq', 'PracIP_BOE', 'PracIP_Gas', 'PrcIPCFGED', 'LatestWtr',
       'Prior12Liq', 'Prior12Gas', 'LastTestDt', 'Prior12Wtr', 'LastFlwPrs',
       'LastWHSIP', '2moGOR', 'LatestGOR', 'CumGOR', 'Lst12Yield', '2moYield',
       'LatestYld', 'PeakGas', 'PkGasMoNo', 'PeakLiq', 'PkLiqMoNo', 'PeakBOE',
       'PkBOEMoNo', 'PkMMCFGE', 'PkMMCFGMoN', 'TopPerf', 'BtmPerf', 'GasGrav',
       'OilGrav', 'CompDate', 'WellCount', 'MaxActvWel', 'GasGather',
       'LiqGather', 'LeaseNo', 'PerfLength', 'TVD', 'Field', 'State',
       'District', 'GeoProvin','Country','OCS_Area', 'PGC_Area',
       'OpReported', 'Survey', 'EntityId', 'Last12Liq', 'Last12Gas',
       'Last12Wtr', 'OtherNo'], inplace = True)

# ### Converting geodataframes to same coord system - UTM system for creating buffers
def convertCRS(*args, crs_system = 26913):
    for i in args:
        print(i.crs)
        i.to_crs(epsg = crs_system, inplace = True)
        print("Converted to:")
        print(i.crs)
        print("\n")

def convertoDateTime(*dataframe):
    '''
    This function will take in arguments of a dataframe.
    It will then search each column name to see if there is a date in the name using the filter method
    The filtered list will then use the apply method to convert data in column to date time
    '''
    for df in dataframe:
        cols = list(filter(lambda x: 'date' in x.lower(), df.columns))

        for col in cols:
            df[col] = df[col].apply(lambda x: pd.to_datetime(x))

#Converting CRS and eate time fields
convertCRS(prodshp, permitshp, leasesgeo, tractshp, oldprod)
convertoDateTime(prodshp, permitshp, leasesgeo, oldprod)

# ### Adding a column to tract shapefile data for centroids of each tract for creating buffers upon
tractshp["centroids"] = tractshp.centroid
#calculating acres of tract, conv to acres is m^2 to acres
tractshp['Acres'] = round(tractshp.area * 0.000247105)

#adding buffer around centroid point from tract of 3 mi (1609.34 meters = 1 mile)

import configparser
config = configparser.ConfigParser()
config.read('/Users/Mishaun_Bhakta/Documents/Python & Projects/Projects/BLM Lease Evaluation and Automation/settings/config.ini')

miradius = config.getint('FILTER', 'mi_radius')
milesbuffer = miradius * 1609.34
tractshp["buffers"] = tractshp.centroids.apply(lambda x: x.buffer(milesbuffer,20))