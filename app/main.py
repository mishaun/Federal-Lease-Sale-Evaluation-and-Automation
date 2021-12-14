# ## Goals of Project
#
# 1. Automate the process of writing notes in a natural language format of each tract in a BLM Oil and Gas Lease Sale
# 2.  Create visualizaitons tract by tract for CEO depicting permitting, new production, and leasing activity within a given radius
# 3.  Create a predictive model to estimate the purchase price based on historical activity, production, permits, and commodity prices

import configparser
import os
config = configparser.ConfigParser()
config_path = '../settings/config.ini'
config.read(config_path)

#changing working directory to sale in config file±
os.chdir(f'../Sales/{config.get("SALE", "sale_dir")}')
print(os.getcwd())

#using from import * to get variables in program memory since functions use global variable names
from app.clean_prep import *
from app.wrangle_filter import *
from app.write_summaries import *

if __name__ == '__main__':

    ### SECTION 1. Loop through cleaned and prepped sale tracts to geospatially filter permits, lease, and production #####3

    # output filtered data for hard storing to excel file
    outputProd = []
    outputPerm = []
    outputLeases = []
    outputOldProd = []

    # looping through each tract id and creating filtered geospatial data
    for i in saleTracts["tract_id"]:
        perm, prod, leases, oldprodtoeval = prepareTractFilter(i, saleTracts, permitsDF, prodDF, leasesDF, oldprodDF)

        # appending geospatial filtered datasets to a list in order to write dataframes to file for easier retrieval and data validaiton
        perm["tract_id"] = i
        outputPerm.append(perm)

        prod["tract_id"] = i
        outputProd.append(prod)

        leases["tract_id"] = i
        outputLeases.append(leases)

        oldprodtoeval["tract_id"] = i
        outputOldProd.append(oldprodtoeval)

    # # ### Writing Filtered Data to File for Easier Retrieval
    # # concatenating filtered dataframes along the row axis and writing to file
    fullFilteredLeases  = pd.concat(outputLeases)
    fullFilteredPermits = pd.concat(outputPerm)
    fullFilteredProd = pd.concat(outputProd)
    fullFilteredOldProd = pd.concat(outputOldProd)

    fullFilteredLeases.to_excel("Output Data/Sale Tracts Activity Data/Leases Around Sale Tracts.xlsx",
                                     index=False)
    fullFilteredPermits.to_excel("Output Data/Sale Tracts Activity Data/Permits Around Sale Tracts.xlsx", index=False)
    fullFilteredProd.to_excel("Output Data/Sale Tracts Activity Data/NewProd Around Sale Tracts.xlsx", index=False)
    fullFilteredOldProd.to_excel("Output Data/Sale Tracts Activity Data/OldProd Around Sale Tracts.xlsx",
                                      index=False)


    ######## SECTION 2: Automating Summaries ####

    #creating empty array to append summaries to for each tract
    summaryPermits = []
    summaryProd = []
    summaryLeases = []
    summaryOldProd = []

    # Looping through sale tracts and pulling data from filtered data sources regarding permits, production, leases
    for i in saleTracts["tract_id"]:
        lease_filtered, permits_filtered, prod_filtered, oldprod_filtered = getActivityData(i, fullFilteredLeases,
                                                                                            fullFilteredPermits,
                                                                                            fullFilteredProd,
                                                                                            fullFilteredOldProd)
    # append summaries to array
        try:
            summaryPermits.append(writePermitSummary(permits_filtered))
        except:
            summaryPermits.append("error occured")

        try:
            summaryProd.append(writeProdSummary(prod_filtered))
        except:
            summaryProd.append("error occured")

        try:
            summaryLeases.append(writeLeaseSummary(lease_filtered))
        except:
            summaryLeases.append("error occured")

        try:
            summaryOldProd.append(writeOldProdSummary(oldprod_filtered, saleTracts, i))
        except:
            summaryOldProd.append("error occured")

    #add columns on sale tract shapefile for summaries written, then export to file
    saleTracts["Permit Summary"] = summaryPermits
    saleTracts["Leases Summary"] = summaryLeases
    saleTracts["Old Production Summary"] = summaryOldProd
    saleTracts["Recent Prod Summary"] = summaryProd

    #Exporting Automated Summaries to File
    saleTracts.drop(columns = "geometry centroids buffers".split(" ")).to_excel("Results/Automated Activity Summary Notes.xlsx", index = False)
