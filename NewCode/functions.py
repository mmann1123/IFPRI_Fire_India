

import os
import numpy as np
import rasterio 
from rasterio.merge import merge
from osgeo import gdal
from xml.dom import minidom
from osgeo import gdal, gdalconst

# Function to select files to be merged. Goes through a folder and writes out a list of unique names
# Uses the unique names to then select appropriate files
def find_unique_days(inpath, name_pattern = ".tif"):
    ending_list = []
    
    # Selects the first part of the file names (ie. MMDDYY)
    for root, dirs, files in os.walk(inpath):
        for filename in files:
            if filename.endswith(name_pattern):
                #print('File name is: {0}'.format(filename))
                ending_list.append(filename.split('_',1)[0])
    
    # Creates a unique day names above to iterate through
    unique_ending = list(set(ending_list))
    print('Unique Dates: {0}'.format(unique_ending))
    
    return(unique_ending)
    

def merge_days(outpath,outname,  files_unique):
    files_mosaic = []
 
    # Opens the files to be merged
    for file in files_unique:
        
        src = rasterio.open(file) 

 
        #if(src.profile['count'] ==4):  not needed anymore 
        print('File '+ file )#+ ' profile ', src.shape, src.profile )
        #only add files with 4 bands
        files_mosaic.append(src)
        # Creates the metadata for the files
        out_meta = src.meta.copy()
    try:
        # Sets the files up to be merged
        mosaic, out_trans = merge(files_mosaic)
        print('mosiac shape:'+ str(mosaic.shape))
        
        
    except:
        print('skipping incompatable image')
        next 

    out_meta.update({"driver": "GTiff",
                  "height": mosaic.shape[1],
                  "width": mosaic.shape[2],
                  "transform": out_trans,
                  'nodata':np.NaN
                  }
                 )
    
    # Writes out the merged raster with the above metadata and a unique name
    outpath_tif = os.path.join(outpath, outname)
    print('#################')
    print('Writing to',outpath_tif)
    with rasterio.open(outpath_tif, "w", **out_meta) as dest:
        dest.write(mosaic)

        
# Function to calculate the Burn Area Index for each raster
def bai_rast_SR(inpath, outpath):
    # Allow division by zero
    np.seterr(divide='ignore', invalid='ignore')
    
    # Opens the raster for the calculation scale to TOA Radiance
    with rasterio.open(inpath) as src:
        red = src.read(3).astype(float) * 0.00001 
        nir = src.read(4).astype(float) * 0.00001 
        
        nir[nir==0] = np.NaN
        red[red==0] = np.NaN
        
        brn_meta = src.profile 
        
    # BAI Formula
    brn_bai = (1 / ((.1-red)**2)+((.06-nir)**2))

    brn_meta.update({"driver": "GTiff",
                  "count":1,
                  "dtype": 'float32',
                  'nodata':np.NaN
                  } )

    # Saves out the raster according to the below criteria
    with rasterio.open(outpath, 'w', **brn_meta) as dst:
        dst.write(brn_bai.astype(rasterio.float32), 1)

        

# Function to calculate the Burn Area Index for each raster
def ndvi_rast_SR(inpath, outpath ):
    
    # Allow division by zero
    np.seterr(divide='ignore', invalid='ignore')
        
    # Opens the raster for the calculation
    with rasterio.open(inpath) as src:
        red = src.read(3).astype(float) * 0.00001 
        nir = src.read(4).astype(float) * 0.00001 
        
        nir[nir==0] = np.NaN
        red[red==0] = np.NaN
        
        ndvi_meta = src.profile 
        

    # NDVI formula
    ndvi =  (nir - red) / (nir + red)

    ndvi_meta.update({"driver": "GTiff",
                  "count":1,
                  "dtype": 'float32',
                  'nodata':np.NaN
                  } )
 
    # Saves out the raster according to the below criteria
    with rasterio.open(outpath, 'w', **ndvi_meta) as dst:
        dst.write(ndvi.astype(rasterio.float32), 1)



# Function to calculate the Burn Area Index for each raster
def bai_rast_MS(inpath, outpath, r2r_dictionary):
    # Allow division by zero
    np.seterr(divide='ignore', invalid='ignore')
    
    # Opens the raster for the calculation scale to TOA Radiance
    with rasterio.open(inpath) as src:
        red = src.read(3).astype(float) * r2r_dictionary[3]
        nir = src.read(4).astype(float) * r2r_dictionary[4]
 
        print('nir band reflectance is '+ str(np.amin(nir))+' '+str(np.median(nir))+ '   '+ str(np.amax(nir)) ) 
        print('red band reflectance is '+ str(np.amin(red))+' '+str(np.median(nir))+ '   '+ str(np.amax(red)) ) 
        
        # remove missing values (0s)
        nir[nir==0] = np.NaN
        red[red==0] = np.NaN
 
        brn_meta = src.profile 
        
    # BAI Formula
    brn_bai = (1 / ((.1-red)**2)+((.06-nir)**2))
   
    print('BAI band reflectance is '+ str(np.amin(brn_bai))+' '+str(np.median(brn_bai))+ '   '+ str(np.amax(brn_bai)) ) 

    #handle outliers
    brn_bai[brn_bai>50000] = 50000
    
    brn_meta.update({"driver": "GTiff",
                  "count":1,
                  "dtype": 'float32',
                  'nodata':np.NaN
                  } )

    # Saves out the raster according to the below criteria
    with rasterio.open(outpath, 'w', **brn_meta) as dst:
        dst.write(brn_bai.astype(rasterio.float32), 1)


# Function to calculate the Burn Area Index for each raster
def ndvi_rast_MS(inpath, outpath, r2r_dictionary):
    
    # Allow division by zero
    np.seterr(divide='ignore', invalid='ignore')
        
    # Opens the raster for the calculation
    with rasterio.open(inpath) as src:
        red = src.read(3).astype(float) * r2r_dictionary[3]
        nir = src.read(4).astype(float) * r2r_dictionary[4]
        
        # remove missing values (0s)
        nir[nir==0] = np.NaN
        red[red==0] = np.NaN
        
        ndvi_meta = src.profile         

    # NDVI formula
    ndvi =  (nir - red) / (nir + red)

    ndvi_meta.update({"driver": "GTiff",
                  "count":1,
                  "dtype": 'float32',
                  'nodata':np.NaN
                  } )
 
    # Saves out the raster according to the below criteria
    with rasterio.open(outpath, 'w', **ndvi_meta) as dst:
        dst.write(ndvi.astype(rasterio.float32), 1)




# Function that merges all the bai rasters as preparation for creating the point grid
def merge_all_rast(outpath, file_list):
    
    files_mosaic =[]
    
    # Opens the files to be merged
    for file in file_list:
        
        src = rasterio.open(file) 

        files_mosaic.append(src)
        # Creates the metadata for the files
        out_meta = src.meta.copy()
    try:
        # Sets the files up to be merged
        mosaic, out_trans = merge(files_mosaic)
        print('mosiac shape:'+ str(mosaic.shape))
        
        
    except:
        print('skipping incompatable image')
        next 

    out_meta.update({"driver": "GTiff",
                  "height": mosaic.shape[1],
                  "width": mosaic.shape[2],
                  "transform": out_trans,
                  'nodata':np.NaN
                  }
                 )
    mosaic.fill(100)
    # Writes out the merged raster with value of zero 
    with rasterio.open(outpath, "w", **out_meta) as dest:
        dest.write(mosaic)
        


def reproject_to_match(image,example_raster, out_name):
    
    # Source
    src_filename = image
    src = gdal.Open(src_filename ) #, gdalconst.GA_ReadOnly)
    print(src)
    src_proj = src.GetProjection()
    
    # We want a section of source that matches this:
    match_filename = example_raster
    match_ds = gdal.Open(match_filename)#, gdalconst.GA_ReadOnly)
    match_proj = match_ds.GetProjection()
    match_geotrans = match_ds.GetGeoTransform()
    wide = match_ds.RasterXSize
    high = match_ds.RasterYSize
    
    # Output / destination
    dst_filename = out_name
    dst = gdal.GetDriverByName('GTiff').Create(dst_filename, wide, high, 1, gdalconst.GDT_Float32)
    dst.SetGeoTransform( match_geotrans )
    dst.SetProjection( match_proj)
    dst.GetRasterBand(1).SetNoDataValue(-9999)
    
    # Do the work
    gdal.ReprojectImage(src, dst, src_proj, match_proj,  gdalconst.GRA_Cubic)
    
    del dst # Flush
    
    
def radiance_2_reflectance(tif_file,):
    # ONLY WORKS WITH MS FILES (NOT SR)
    #https://developers.planet.com/tutorials/convert-planetscope-imagery-from-radiance-to-reflectance/
    
    base=os.path.splitext(os.path.basename(tif_file))[0]
    path = os.path.dirname(tif_file)
    xmldoc = minidom.parse(os.path.join(path,base+'_metadata.xml'))
    nodes = xmldoc.getElementsByTagName("ps:bandSpecificMetadata")

    # XML parser refers to bands by numbers 1-4
    coeffs = {}
    for node in nodes:
        bn = node.getElementsByTagName("ps:bandNumber")[0].firstChild.data
        if bn in ['1', '2', '3', '4']:
            i = int(bn)
            value = node.getElementsByTagName("ps:reflectanceCoefficient")[0].firstChild.data
            coeffs[i] = float(value)
    return coeffs


 ## A funciton that reprojects the rasters to match blank raster properties 
#def reproject_rast( in_image, out_path, example_raster):
#    
 
      # NOT WORKING 
#    # Desired CRS (wgs84 UTM zone 43N)
#    dst_crs = 'EPSG:32643'  
#
#    # opens blank raster and copies properties 
#    with rasterio.open( example_raster ) as example:
#        example.kwargs = example.meta.copy()
#    
#    # Opens the raster to be reprojected
#    with rasterio.open(in_image,'r+') as src:
#        transform, width, height = calculate_default_transform(
#            src.crs, dst_crs, src.width, src.height, *src.bounds)
#        kwargs = src.meta.copy()
#        kwargs.update({
#            'crs': dst_crs,
#            'transform': transform,
#            'width': width,
#            'height': height
#        })
#        
#        # Reprojects the raster
#        with rasterio.open(out_path, 'w', **kwargs) as dst:
#                for i in range(1, src.count + 1):
#                    reproject(
#                        source=rasterio.band(src, i),
#                        destination=rasterio.band(dst, i),
#                        src_transform=src.transform,
#                        src_crs=src.crs,
#                        dst_transform=transform,
#                        dst_crs=dst_crs,
#                        resampling=Resampling.nearest)
#
## Function to search through folders to select files to be reprojected
#all_images = glob(os.path.join(inpath,'**/*ndvi.tif'))+glob(os.path.join(inpath,'**/*bai.tif'))
#example_raster = r"C:\Users\mmann\Dropbox\IFPRI_Fire_India\Images_new\combine\all_merge_clip.tif"
#
#
#for image in all_images:
#    out_name = os.path.join(inpath,'reproject', os.path.basename(image) )
#    reproject_rast( in_image = image, out_path = out_name, example_raster=example_raster)
