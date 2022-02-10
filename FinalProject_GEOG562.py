### GEOG 562
### Final Project
### Kaden Flick and Kira Minehart
### June 2021

### All code in this file prepared by Kira Minehart

### Part 0 --------------------------------------------------------------------------------------------------------
### PREPARE ENVIRONMENT

# import required packages
import sys
import arcpy
from arcpy import env
from arcpy.sa import *
import os

# set workspace
arcpy.env.workspace = 'Final Project'
CurrentWorkspace = arcpy.env.workspace
path = sys.path[0]

# allow file overwrite
arcpy.env.overwriteOutput = True


### Part 1 --------------------------------------------------------------------------------------------------------
### LOAD DATA

# Protected areas shapefile (GAP status 1 and 2)
protected = 'OR_protected.shp'

### Part 2 --------------------------------------------------------------------------------------------------------
### CLIP  DATA TO STUDY AREA (Kaden)

# This part is accomplished using Kaden's code compiled in the bulk_clipping files as well as the supporting functions
# files. Part 2 must be completed before moving onto part 3 to generate the required files.
# See the following files: bulk_clip_step1.py, bulk_clip_step2.py

### Part 3 --------------------------------------------------------------------------------------------------------
### COMPUTE SPATIAL STATISTICS FOR LAND COVER CHANGE PIXELS FOR EACH DATASET

# load required extension
arcpy.CheckOutExtension("Spatial")

# define paths for folders to store the data
clippedpath = path + '/Clipped_rasters'
outpath = path + '/LCC_rasters'
export_gdb = 'Export_GDB.gdb'

# list comprehension to access of the clipped .tif files from kaden's output
files = [file for file in os.listdir(clippedpath) if file.lower().endswith('.tif')]

# for loop to perform LCC analysis on each .tif file
for file in files:

    # set the current workspace and outpath
    CurrentWorkspace = arcpy.env.workspace
    arcpy.env.workspace = outpath
    arcpy.env.overwriteOutput = True

    # define infile
    infile = clippedpath + '/' + file
    # rename the outfile, keeping the year
    print("test0")
    outfile = outpath + '/' + file.split(".")[0] + "_LCC"

# if the file does not already exist, try the following:
    if not arcpy.Exists(outfile):
        # set the infile
        inraster = arcpy.Raster(infile)
        # extract pixels that represent LCC (Values 9 - 87, see metadata)
        outraster = arcpy.sa.ExtractByAttributes(in_raster=inraster, where_clause="VALUE > 8 AND VALUE <88")
        # export intermediate outfile to geodatabase
        inter_outfile = export_gdb + "/" + file.split(".")[0] + "_LCC"
        # save the outfile
        outraster.save(inter_outfile)
        # create a final file to be stored as a raster in LCC_rasters folder
        final_outfile = outpath + "/" + file.split(".")[0] + "_LCC." + file.split(".")[-1]
        # copy the output files to the LCC_raster location
        arcpy.management.CopyRaster(outraster, final_outfile)

        # prepare file for summary statistics
        stat_file = arcpy.Raster(outraster)

        # compute summary statistics, stored to .dbf in LCC_rasters folder
        arcpy.analysis.Statistics(in_table=stat_file, out_table= arcpy.Raster(final_outfile),
                                  statistics_fields=[["Value", "SUM"]], case_field=[])

        # confirmation statement to ensure process executed
        print("Extract land cover change pixels from " + final_outfile)

        # reset the workspace
        arcpy.env.workspace = CurrentWorkspace
        arcpy.env.overwriteOutput = True

    else:
        print("File already exists: " + outfile)

