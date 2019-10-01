# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 16:22:48 2019

@author: MMann
"""
import os
import rasterio
from rasterio.merge import merge
from shapely.geometry import mapping, Polygon, Point
from rasterio import features
import fiona
from fiona.crs import from_epsg
from osgeo import gdal
import ogr, osr
from osgeo import ogr
import csv
import geojson
import json
import pandas
from rasterstats import raster_stats
from glob import glob
import matplotlib.pyplot as plt
%matplotlib inline
from sklearn.metrics import accuracy_score,confusion_matrix, cohen_kappa_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import tsraster.model  as md
import pandas as pd
from rasterio.warp import calculate_default_transform, reproject, Resampling
from tsraster.calculate import calculateFeatures
import seaborn as sb
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler

#%%
os.chdir(r'C:\Users\mmann\Dropbox\IFPRI_Fire_India\NewCode')

from functions import merge_rast, 

test()

#%%