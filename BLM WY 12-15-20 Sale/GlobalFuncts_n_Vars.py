#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 13:51:27 2020

@author: Mishaun_Bhakta
"""

#These functions are copied from jupyter notebook 
# ** changes to functions should be made in the notebook then copied here

import pandas as pd
import geopandas as gp
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import shapely
import math
import datetime as dt
import pdb


#Global Vars

#radius for evaluation
miradius = 3
milesbuffer = miradius * 1609.34

#Sale Date
saleDate = pd.Timestamp(dt.date(2020, 3, 23))

#creating list of columns for learning variables on particular lease
learningCols = ["Total Permits", "Total Wells", "Avg First 6 Mo Oil", "Avg First 6 Mo Gas", "Qi Oil", "Qi Gas", "6 Mo Oil Revenue $", "6 Mo Gas Rev $", "Oil Price", "Gas Price" ]

#Prices
#get historical oil price data
oilPrices = pd.read_excel("Data/oilPrices.xls", sheet_name="Data 1", header=2)

#renaming price column to something more concise 
oilPrices.rename(columns = {'Cushing, OK WTI Spot Price FOB (Dollars per Barrel)' : "WTI Price"} , inplace = True)

#appending data to the data frame for missing months manually - setting march 2020 price to $25/bbl
oilPrices = oilPrices.append({'Date': pd.to_datetime('2020-03-15', format='%Y-%m-%d', errors='ignore'), 'WTI Price': 25}, ignore_index = True)

#Setting the index of the dataframe as the date and then filtering to data within last 10 years
oilPrices.set_index("Date", inplace = True)
oilPrices = oilPrices.loc[oilPrices.index.year > 1999] 

#get historical gas price data
gasPrices = pd.read_excel("Data/gasPrices.xls", sheet_name="Data 1", header=2)

gasPrices.set_index('Date', inplace = True)
gasPrices.rename(columns = {'Henry Hub Natural Gas Spot Price (Dollars per Million Btu)': 'Gas Price'}, inplace = True)
gasPrices = gasPrices.loc[gasPrices.index.year > 1999] 

# Global Functions

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
            
def getTrainingMeasures(LeasesForEval, leaseIndex, trainProd, trainPermits):
    
    '''
    This function will take in 3 dataframes
    1. LeasesForEval will be the cleaned dataframe that holds lease information with bonus prices
    2. trainProd is the cleaned dataframe that holds production necessary for evaluating leases
    3. trainPermits is the cleaned dataframe that holds permits necessary for evaluating leases
    
    The function will take in an index from the LeasesForEval to perform the following actions:
        - The fuction will filter and retrieve permit and production data within a 3 mile radius from the lease point
        - It will also find the oil/gas price for the month the lease was recorded
        - Filters will be applied to the found permit and production data in order to get a snapshot of the data that existed during the time of purchasing the lease
        - Measures such as average First 6 month oil production and total number of wells will be stored in columns as the inputs (x vars) for the ML model
    '''
    
    #Getting single lease from data 
    leaseDf = LeasesForEval.loc[LeasesForEval.index == leaseIndex]
    leaseDf = leaseDf.iloc[0]
    
    
    #pulling date from lease for evaluations to create filter on permit and prod datasets
    filterDate = leaseDf["Record Date"]

    #filtering production dataframe to within buffer of lease for evaluation & only wells taht had started producing before the date lease was recorded
    prodFilter = trainProd.loc[trainProd.within(leaseDf["buffers"])]
    prodFilter = prodFilter.loc[prodFilter["FstPrdDate"] <= filterDate]

    #filtering permit dataframe to within buffer of lease for evaluation & only permits that were active time of the lease
    permFilter = trainPermits.loc[trainPermits.within(leaseDf["buffers"])]

    #creating a filter to only show active permits within time lease was purchased
    permFilter = permFilter.loc[(permFilter["ExpDate"]>=filterDate) & (permFilter["AprvdDate"]<=filterDate)]

    #saving learning variable: total number of active permits
    totalActivePermits = len(permFilter)
    
    #finding month in oil and gas price dataframes based on record date of lease
    #formatting data to find by month and year only
    searchMonthYr = "{}-{}".format(filterDate.month, filterDate.year)

    #saving gas and oil price from the time of the record date of the lease
    oilPriceYr = oilPrices.loc[searchMonthYr]["WTI Price"].iloc[0]
    gasPriceYr = gasPrices.loc[searchMonthYr]["Gas Price"].iloc[0]
    
    #getting variables to learn on from production dataframe
    totalWells = len(prodFilter)
    Avg6MoOilProd = prodFilter["6moLiq"].mean()
    Avg6MoGasProd = prodFilter["6moGas"].mean()

    #multiplying Initial production daily rates for the given month by 30 to get it into a Qi monthly rate
    IPoil = prodFilter["PracIP_Liq"].mean() * 30
    IPgas = prodFilter["PracIP_Gas"].mean() * 30
    
    First6MoOilRev = Avg6MoOilProd*oilPriceYr
    First6MoGasRev = Avg6MoGasProd*gasPriceYr
    
    #making a list of all the learning variables saved
    learningVals = [totalActivePermits, totalWells, Avg6MoOilProd,Avg6MoGasProd, IPoil, IPgas, First6MoOilRev, First6MoGasRev, oilPriceYr, gasPriceYr]


    #zipping learning value with the column name it belongs to as a tuple pair
    learningPairs = list(zip(learningCols, learningVals))
    
    #appending learning value to its corresponding dataframe column for the given lease
    for pair in learningPairs:
        LeasesForEval.loc[LeasesForEval.index == leaseIndex, pair[0]] = pair[1]
    
    #storing state of filter in order to review for quality assurance - will append to list when function is called in loop
    permFilter["LeaseIndex"] = leaseIndex
    prodFilter["LeaseIndex"] = leaseIndex
    
    return permFilter, prodFilter