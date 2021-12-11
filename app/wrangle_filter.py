# ## Goals of Module
# 1.  Write function to filter data in defined mile radius for each tract in sale
# 2.  Export filtered data for sale note generationa



# function to get compass direction
def cardDir(point, tractRef):
    '''
    This function will take in 2 inputs and will calculate the cardinal direction between 2 points

    1.  point: a shapely Point object referring to a permit,lease, well found in spatial query
    2.  tractRef: a shapely Point object referring to the centroid of the lease/tract for analysis
    '''

    # storing each coordinate in a temporary variable
    a = point.x
    b = point.y
    c = tractRef["centroids"].x
    d = tractRef["centroids"].y

    # south and west are positive direction for my axis convention
    western = c - a
    southern = d - b

    # calculating angle between points for determining which direction the point of data is in reference to tract centroid
    compdeg = abs(math.atan(western / southern))
    # converts radians to degrees
    compdeg *= 57.2958
    compdeg

    if southern > 0:
        if compdeg < 10:
            carddir = "S"
        elif compdeg > 80:
            if western > 0:
                carddir = "W"
            else:
                carddir = "E"
        else:
            if western > 0:
                carddir = "SW"
            else:
                carddir = "SE"
    else:
        if compdeg < 10:
            carddir = "N"
        elif compdeg > 80:
            if western > 0:
                carddir = "W"
            else:
                carddir = "E"
        else:
            if western > 0:
                carddir = "NW"
            else:
                carddir = "NE"

    return carddir


# ### Creating Function from Test Above and Below Code to Get Filtered Data Tract by Tract In a Loop

def prepareTractFilter(x):
    '''This function will use global variables defined previously for testing each tract
       x will be the tract number we will look for activity around

       The functinon will run and add columns of data only necessary for the filtered values data
    '''

    # getting tract in sale list to search well data (permits, leases, prod)
    tractTest = tractshp[tractshp["tract_id"] == x].iloc[0]

    # global variables permitshp, prodshp, leasesgeo - not passing them into the function
    # this will use geopandas function within to get data within buffer of test tract and then use the boolean array to filter itself to get data
    permitstoeval = permitshp.loc[permitshp.within(tractTest["buffers"])]
    prodtoeval = prodshp.loc[prodshp.within(tractTest["buffers"])]
    leasestoeval = leasesgeo.loc[leasesgeo.within(tractTest["buffers"])]
    oldprodtoeval = oldprod.loc[oldprod.within(tractTest["buffers"])]

    # calculating distance (in miles) away lease within 3 mi radius is to tract of interest and direction of data point (permit, lease, prod)
    leasestoeval["distance"] = leasestoeval["geometry"].apply(lambda x: x.distance(tractTest["centroids"]) / 1609.34)
    leasestoeval["direction"] = leasestoeval["geometry"].apply(lambda x: cardDir(x, tractTest))
    leasestoeval["RecordYr"] = leasestoeval["Record Date"].apply(lambda x: x.year)

    # adding columns to permits dataframe such as horizontal lngth and direction
    permitstoeval["horzLength"] = permitstoeval["PermDepth"] - permitstoeval["TVD"]
    permitstoeval["distance"] = permitstoeval["geometry"].apply(lambda x: x.distance(tractTest["centroids"]) / 1609.34)
    permitstoeval["direction"] = permitstoeval["geometry"].apply(lambda x: cardDir(x, tractTest))

    prodtoeval["distance"] = prodtoeval["geometry"].apply(lambda x: x.distance(tractTest["centroids"]) / 1609.34)
    prodtoeval["direction"] = prodtoeval["geometry"].apply(lambda x: cardDir(x, tractTest))

    oldprodtoeval["distance"] = oldprodtoeval["geometry"].apply(lambda x: x.distance(tractTest["centroids"]) / 1609.34)
    oldprodtoeval["direction"] = oldprodtoeval["geometry"].apply(lambda x: cardDir(x, tractTest))

    return permitstoeval, prodtoeval, leasestoeval, oldprodtoeval


def wrangle_and_export(tractsshp):
    # ### Looping Through All Sale Tracts - Retrieving Data Around Tract
    # output filtered data for hard storing to excel file
    outputProd = []
    outputPerm = []
    outputLeases = []
    outputOldProd = []

    # looping through each tract id and creating filtered geospatial data, activity summaries, and visualizaiton plots
    for i in tractshp["tract_id"]:
        perm, prod, leases, oldprodtoeval = prepareTractFilter(i)

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
    pd.concat(outputLeases).to_excel("Output Data/Sale Tracts Activity Data/Leases Around Sale Tracts.xlsx", index=False)
    pd.concat(outputPerm).to_excel("Output Data/Sale Tracts Activity Data/Permits Around Sale Tracts.xlsx", index=False)
    pd.concat(outputProd).to_excel("Output Data/Sale Tracts Activity Data/Prod Around Sale Tracts.xlsx", index=False)
    pd.concat(outputOldProd).to_excel("Output Data/Sale Tracts Activity Data/OldProd Around Sale Tracts.xlsx", index=False)



if __name__ == '__main__':
    from clean_prep import *

    # # Testing Spatial Filters
    try:
        TestT = 1
        tractTest = tractshp[tractshp["tract_id"] == TestT].iloc[0]

        permFiltered = permitshp.loc[permitshp.within(tractshp[tractshp["tract_id"] == TestT]["buffers"].iloc[0])]
        prodFiltered = prodshp.loc[prodshp.within(tractshp[tractshp["tract_id"] == TestT]["buffers"].iloc[0])]
        leasesFiltered = leasesgeo.loc[leasesgeo.within(tractshp[tractshp["tract_id"] == TestT]["buffers"].iloc[0])]
    except:
        print('test failed')

    len(permFiltered), len(prodFiltered), len(leasesFiltered)

    wrangle_and_export()

    # ### Looping Through All Sale Tracts - Retrieving Data Around Tract
    # output filtered data for hard storing to excel file
    outputProd = []
    outputPerm = []
    outputLeases = []
    outputOldProd = []

    # looping through each tract id and creating filtered geospatial data, activity summaries, and visualizaiton plots
    # for i in tractshp["tract_id"]:
    #     perm, prod, leases, oldprodtoeval = prepareTractFilter(i)
    #
    #     # appending geospatial filtered datasets to a list in order to write dataframes to file for easier retrieval and data validaiton
    #     perm["tract_id"] = i
    #     outputPerm.append(perm)
    #
    #     prod["tract_id"] = i
    #     outputProd.append(prod)
    #
    #     leases["tract_id"] = i
    #     outputLeases.append(leases)
    #
    #     oldprodtoeval["tract_id"] = i
    #     outputOldProd.append(oldprodtoeval)
    #
    # # ### Writing Filtered Data to File for Easier Retrieval
    #
    # # concatenating filtered dataframes along the row axis and writing to file
    # pd.concat(outputLeases).to_excel("Output Data/Sale Tracts Activity Data/Leases Around Sale Tracts.xlsx", index=False)
    # pd.concat(outputPerm).to_excel("Output Data/Sale Tracts Activity Data/Permits Around Sale Tracts.xlsx", index=False)
    # pd.concat(outputProd).to_excel("Output Data/Sale Tracts Activity Data/Prod Around Sale Tracts.xlsx", index=False)
    # pd.concat(outputOldProd).to_excel("Output Data/Sale Tracts Activity Data/OldProd Around Sale Tracts.xlsx", index=False)
