#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import geopandas as gp
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import shapely


prod = pd.read_csv("Data/Production Table.CSV")
perm = pd.read_csv("Data/PermitsTable.CSV")
leases = pd.read_csv("Data/LeasesTable.CSV")

#had to add GDAL_DATA variable to system variables and set value to the folder of gdal in C:\Users\mishaun\AppData\Local\Continuum\anaconda3\Library\share\gdal on my work computer
shapezipfile = ("zip://Data/BLMWY-2020-Q1-3_WGS84.zip")
shapedf = gp.read_file(shapezipfile, encoding = "utf-8")

import os

'GDAL_DATA' in os.environ

shapedf.crs


#converting crs to drillinginfo coord system
shapedf.to_crs(epsg = 4326, inplace = True)


shapedf["centroids"] = shapedf.centroid


shapedf.head()


# latlongs = prod[["Surface Latitude (WGS84)", "Surface Longitude (WGS84)"]]

# latlongs = gp.GeoDataFrame(latlongs, crs = coordSystem, geometry=gp.points_from_xy(latlongs.iloc[:,1], latlongs.iloc[:,0]))

# ## Shapefile Downloads from DI


#this is shapefile downloaded from drillinginfo holding well information
prodshp = gp.read_file("zip://Data/production.ZIP")


permitshp = gp.read_file("zip://Data/production.ZIP")
permitshp.crs

leasesgeo = gp.read_file("Data/LeasesTable.CSV")

converse = permitshp[permitshp["County"]=="CONVERSE (WY)"]


converse.plot()


shapedf.crs


shapedf.plot()





