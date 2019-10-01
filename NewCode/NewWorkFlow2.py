# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 14:23:29 2019

@author: mmann
"""

import os
import rasterio
import fiona
from glob import glob
#%matplotlib inline
from rasterio.warp import calculate_default_transform, reproject, Resampling
#import seaborn as sb
from itertools import chain
from functions import merge_days, bai_rast, ndvi_rast, merge_all_rast,find_unique_days,reproject_to_match
import rasterio.mask
import geopandas as gpd


#%%
os.chdir(r'C:\Users\mmann\Dropbox\IFPRI_Fire_India\NewCode')
inpath = "../Images_new"

#%%

find_unique_days(inpath)

#%%

# Calculate NDVI and BAI 
inpath = "../Images_new"

name_pattern ='SR.tif'
unique_days = find_unique_days(inpath, name_pattern )
bad_patterns = ['*DN_udm.tif','*merge.tif','*MS.tif']


# create NDVI and BAI for each day 
for unique_day in unique_days:
    # get all images for day
    a_day_images = list(set(glob(os.path.join(inpath,'**/*'+ unique_day+'*'+name_pattern))))

    # remove all unwanted
    images_2_remove = [glob(os.path.join(inpath, '**/*'+unique_day+bad)) for bad in bad_patterns]
    images_2_remove = list(set(chain(*images_2_remove))) # unlist of lists 
    a_day_images_filtered = list(set(a_day_images) - set(images_2_remove))
    
    iterator = 0
    
    for an_image in a_day_images_filtered:
        
        bai_rast(inpath=an_image, 
                 outpath=os.path.join(inpath,'bai',unique_day+"_"+str(iterator) + "_bai.tif"))
        
        ndvi_rast(inpath=an_image, 
                 outpath=os.path.join(inpath,'ndvi',unique_day +"_"+str(iterator) + "_ndvi.tif"))
        iterator= iterator + 1 


#%%


# MERGE SAME DAYS: Iterates through the unique list to select where files contain the same name and sets them up to be merged


# find all ndvi tifs 
name_pattern ='ndvi.tif'
unique_days = find_unique_days(inpath, name_pattern )
bad_patterns = ['*DN_udm.tif','*merge.tif','*MS.tif']

# merge by day 
for unique_day in unique_days:
    # get all images for day
    a_day_images = list(set(glob(os.path.join(inpath,'**/*'+ unique_day+'*'+name_pattern))))

    # remove all unwanted
    images_2_remove = [glob(os.path.join(inpath, '**/*'+unique_day+bad)) for bad in bad_patterns]
    images_2_remove = list(set(chain(*images_2_remove))) # unlist of lists 
    a_day_images_filtered = list(set(a_day_images) - set(images_2_remove))
    
    # merge same days 
    merge_days(outpath  = "../Images_new/merge", 
               outname =   unique_day + "_ndvi_merge.tif",
               files_unique = a_day_images_filtered)



# find all bai tifs 
name_pattern ='bai.tif'
unique_days = find_unique_days(inpath, name_pattern )
bad_patterns = ['*DN_udm.tif','*merge.tif','*MS.tif']

# merge by day 
for unique_day in unique_days:
    # get all images for day
    a_day_images = list(set(glob(os.path.join(inpath,'**/*'+ unique_day+'*'+name_pattern))))

    # remove all unwanted
    images_2_remove = [glob(os.path.join(inpath, '**/*'+unique_day+bad)) for bad in bad_patterns]
    images_2_remove = list(set(chain(*images_2_remove))) # unlist of lists 
    a_day_images_filtered = list(set(a_day_images) - set(images_2_remove))
    
    # merge same days 
    merge_days(outpath  = "../Images_new/merge", 
               outname =   unique_day + "_bai_merge.tif",
               files_unique = a_day_images_filtered)

#%%





#%%


#%% Create blank example raster with full extent of all images 


# Selects the files using a unique identifier and sets up the out paths
 
all_bai = glob(os.path.join(inpath,'**/*ndvi_merge.tif'))
outpath = os.path.join(inpath ,'combine', "all_merge.tif")


merge_all_rast(outpath, file_list=all_bai)

#%% Clip merged raster to shapefile 


gdf= gpd.read_file(r"C:\Users\mmann\Dropbox\IFPRI_Fire_India\Shapefiles\right_cluster.geojson")
gdf = gdf.to_crs({'init': 'epsg:32643'})
gdf.to_file(r"C:\Users\mmann\Dropbox\IFPRI_Fire_India\Shapefiles\right_cluster_projected.geojson", driver='GeoJSON')

with fiona.open(r"C:\Users\mmann\Dropbox\IFPRI_Fire_India\Shapefiles\right_cluster_projected.geojson", "r") as shapefile:
    print(shapefile.crs)
    feature = [feature["geometry"] for feature in shapefile]


with rasterio.open(os.path.join(inpath ,'combine', "all_merge.tif")) as src:
    out_image, out_transform = rasterio.mask.mask(src, feature,
                                                        crop=True)
    out_meta = src.meta.copy()

out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
        
with rasterio.open(os.path.join(inpath ,'combine', "all_merge_clip.tif"), "w", **out_meta) as dest:
    dest.write(out_image)



#%%
         


#%% reproject attempt 2 
from osgeo import gdal, gdalconst


for image in all_images:
    all_images = glob(os.path.join(inpath,'**/*ndvi_merge.tif'))+glob(os.path.join(inpath,'**/*bai_merge.tif'))
    example_raster = r"C:\Users\mmann\Dropbox\IFPRI_Fire_India\Images_new\combine\all_merge_clip.tif"
    out_name = os.path.join(inpath,'reproject', os.path.basename(image) )
    reproject_to_match(inpath,example_raster, out_name)
    

# manual resort them to NDVI and BAI folders
    
#%%
    
    
    