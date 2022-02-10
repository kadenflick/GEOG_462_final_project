#********************************************
# This file contains the supporting functions that drive the bulk_clipping
# functions.
#
# This code written by Kaden Flick
# GEOG 462 - Spring 2021
#********************************************

import json, os.path, arcpy
import tkinter as tk
import tkinter.filedialog as tkfd

# A function to collect all the necessary information to format the JSON files
def get_user_info (save_dict):
    # Ask for a name for batch JSON
    print("Please enter a name for this batch:")
    filename = input(">>> ")

    # Set up tkinter window
    window = tk.Tk()
    window.attributes('-topmost', True)
    window.lift()
    window.withdraw()


    # Get raster_directory
    print("\nSelect raster files to clip. Hold control to select muiltple files.")

    list_filetypes = (("All files","*.*"), ("ESRI BIL files","*.bil"), ("ESRI BIP files","*.bip"), ("BMP files","*.bmp"),
                      ("ESRI BSQ files","*.bsq"), ("ENVI DAT files","*.dat"), ("GIF files","*.gif"),
                      ("ERDAS IMAGINE files","*.img"), ("JPEG files","*.jpg"), ("JPEG 2000 files","*.jp2"),
                      ("PNG files","*.png"), ("TIFF files","*.tif"), ("MRF files","*.mrf"), ("CRF files","*.crf"))
    temp = tkfd.askopenfilenames(parent = window, initialdir = '/', title = 'Select Raster Files', filetypes = list_filetypes)
    save_dict.update({'raster_files': temp})

    # Get polygon_directory
    print("Select polygon files to clip to. Hold control to select muiltple files.")

    list_filetypes = (("SHP files","*.shp"), ("All files","*.*"))
    temp = tkfd.askopenfilenames(parent = window, initialdir = '/', title = 'Select Polygon Files', filetypes = list_filetypes)
    save_dict.update({'polygon_files': temp})

    # Get output_directory
    print("Select directory to save files to.")

    temp = tkfd.askdirectory(parent = window, initialdir = '/', title = 'Select Output Directory')
    save_dict.update({'output_directory': temp})

    window.destroy()


    # Print some instructions
    print("\nFor the following inputs defaults have been set. To use a default value, enter '#' when prompted.\n")

    # Get output_extentsion
    print("Output raster formats:\n"
        "\t[1] ESRI BIL files\n\t[2] ESRI BIP files\n\t[3] BMP files\n\t[4] ESRI BSQ files\n"
        "\t[5] ENVI DAT files\n\t[6] GIF files\n\t[7] ERDAS IMAGINE files\n\t[8] JPEG files\n\t[9] JPEG 2000 files\n"
        "\t[10] PNG files\n\t[11] TIFF files\n\t[12] MRF files\n\t[13] CRF files\n\t[#] Default")

    print("Select format for clipped raster images: ")
    temp = check_option_list(1, 13)

    type_options = ['.bil','.bip','.bmp','.bsq','.dat','.gif','.img','.jpg','.jp2','.png','.tif','.mrf','.crf']

    if temp != '#':
        save_dict.update({'output_extentsion': type_options[int(temp) - 1]})


    # Get nodata_value
    print("\nEnter NoData value: ")
    temp = input(">>> ")

    if temp != '#':
        save_dict.update({'nodata_value': temp})


    # Get maintain_clipping_extent
    print("\nMaintain Clipping Extent options:\n"
        "\t[1] Maintain clipping extent\n\t[2] Don't maintain clipping extent\n\t[#] Default")

    print("Select option to maintain clipping extent: ")
    temp = check_option_list(1, 2)

    maintain_options = ['MAINTAIN_EXTENT','NO_MAINTAIN_EXTENT']

    if temp != '#':
        save_dict.update({'maintain_clipping_extent': maintain_options[int(temp) - 1]})

    # Return created dictionary and filename
    return save_dict, filename

# A function that checks to see if input from a list of options is acceptable
def check_option_list (low, high):
    # Prompt for input
    temp = input(">>> ")

    # Check if input is valid. If not, get new input
    while True:
        if temp == '#' or low <= int(temp) <= high:
            break
        else:
            print("Input not valid")
            temp = input(">>> ")

    # Return proper input
    return temp

# A function that checks if yes or no was entered
def check_yes_no ():
    while True:
        # Prompt for input
        temp = input(">>> ")

        # Check if input is valid. If not, get new input
        if temp == 'y' or temp == 'n' or temp == 'Y' or temp == 'N':
            break
        else:
            print("That is not a valid input.")

    # Return proper input
    return temp

# A function to save JSON files in a dictionary
def parse_json (json_file):
    # Open file and dump save contents of JSON to a dictionary
    with open(json_file, 'r') as infile:
        temp_dict = json.load(infile)

        print("Successfully loaded {}".format(infile.name))

    # Return dictionary
    return temp_dict

# A function to perform clipping operations based on passed dictionary
def bulk_clipping (param_dict):
    # Check if the output directory exists. If not, return message and quit
    if not os.path.exists(param_dict['output_directory']):
        return -1, 'Output directory does not exist'

    # Find any indexes from raster or polygon lists that do not exist. Save indexes of those that do not exist
    raster_skip, polygon_skip, success, message = find_missing_indexes(param_dict)

    # Outer loop to iterate through all of the rasters in the dictionary
    for current_raster in param_dict['raster_files']:
        # If the raster at this index is not in the list of indexes to skip
        if param_dict['raster_files'].index(current_raster) not in raster_skip:
            # Clip the raster to each one of the polygons in the dictionary
            for current_polygon in param_dict['polygon_files']:
                # Only clip if the current polygon is also not on the list of skipped polygons
                if param_dict['polygon_files'].index(current_polygon) not in polygon_skip:

                    # Get in_raster
                    in_raster = current_raster

                    # Get bounding rectangle
                    ok, rectangle = bounding_rectangle(current_polygon)
                    # Throw error and skip loop if something went wrong
                    if ok != 1:
                        success = -1
                        message = message + rectangle
                        continue

                    # Get out_raster based on filepaths of current raster and polygon
                    basename = os.path.basename(current_polygon)
                    current_polygon_name = os.path.splitext(basename)[0]

                    basename = os.path.basename(current_raster)
                    current_raster_name = os.path.splitext(basename)[0]

                    out_raster = """{}\{}_CLIP_{}{}""".format(param_dict['output_directory'], current_polygon_name, current_raster_name, param_dict['output_extentsion'])

                    # Get in_template_dataset
                    in_template_dataset = current_polygon

                    # Get nodata_value
                    nodata_value = param_dict['nodata_value']

                    # Get clipping_geometery
                    clipping_geometery = 'ClippingGeometry'

                    # Get maintain_clipping_extent
                    # If polygon is the last one to clip the raster to, set maintain extent to desired setting
                    if param_dict['polygon_files'].index(current_polygon) == len(param_dict['polygon_files']):
                        maintain_clipping_extent = param_dict['maintain_clipping_extent']
                    # If not, keep original raster extent so we can keep clipping
                    else:
                        maintain_clipping_extent = 'MAINTAIN_EXTENT'

                    # Call function to clip raster
                    ok, clip_message = clip_raster(in_raster, rectangle, out_raster, in_template_dataset, nodata_value, clipping_geometery, maintain_clipping_extent)
                    # Throw error and skip loop if something went wrong
                    if ok != 1:
                        success = -1
                        message = message + clip_message
                        continue

                    print("Sucessfully clipped {}\n".format(out_raster))

    # Return where or not clipping was successful and any messages
    return success, message

# A function to clip rasters
def clip_raster (in_raster, rectangle, out_raster, in_template_dataset, nodata_value, clipping_geometery, maintain_clipping_extent):
    try:
        # Create path and filename for the reprojected raster - This is to handle rasters and polygons in different projections
        directory = os.path.dirname(os.path.abspath(in_raster))
        raster_name = os.path.splitext(os.path.basename(in_raster))[0]
        poly_projection = os.path.splitext(os.path.basename(in_template_dataset))[0]
        extension = os.path.splitext(os.path.basename(out_raster))[1][0:4]
        projection_raster = r'{}\{}_PROJ_{}{}'.format(directory, raster_name, poly_projection, extension)

        print("Reprojecting {}...".format(os.path.basename(in_raster)))

        # If a projected raster already exists, delete it
        if os.path.exists(projection_raster):
            os.remove(projection_raster)

        # Reproject raster to polygon's projected coordinate system
        arcpy.ProjectRaster_management(in_raster, projection_raster, in_template_dataset)

        print("Clipping {} to {}...".format(os.path.basename(in_raster), os.path.basename(in_template_dataset)))

        # If clipped raster already exists, delete it
        if os.path.exists(out_raster):
            os.remove(out_raster)

        # Clip raster to polygon extent
        arcpy.Clip_management(projection_raster, rectangle, out_raster, in_template_dataset, nodata_value, clipping_geometery, maintain_clipping_extent)

        # Remove reprojectd raster
        os.remove(projection_raster)
    except Exception as err:
        # If something goes wrong, capture error and quit
        return -1, 'Something went wrong with the clip for {}.\nError: {} '.format(out_raster, err.args[0])

    # If sucessful, return
    return 1, ""

# A function to find any polygons or rasters that might not exist
def find_missing_indexes (param_dict):
    # Save indexes of rasters and polygons that don't exist
    raster_skip = [param_dict['raster_files'].index(path) for path in param_dict['raster_files'] if not os.path.exists(path)]
    polygon_skip = [param_dict['polygon_files'].index(path) for path in param_dict['polygon_files'] if not os.path.exists(path)]

    success = 1
    message = ""
    raster_message = ""
    polygon_message = ""

    # If indexes to skip were found, create messages
    if len(raster_skip) != 0:
        success = -1
        raster_message = 'One or more raster files cannot be located. '

    if len(polygon_skip) != 0:
        success = -1
        polygon_message = 'One or more polygon files cannot be located. '

    # If indexes to skip were found, concatenate messagaes
    if success != 1:
        message = raster_message + polygon_message + 'An attempt was made to process with existing files, but output may not be correct. '

    # Return indexes to skip and any messages
    return raster_skip, polygon_skip, success, message

# A function to find the bounding rectangle of a polygon - based on Lab 6 code
def bounding_rectangle (polygon):
    try:
        # Describe polygon
        shape = arcpy.Describe(polygon)

        # Get bounding rectangle
        xmin = str(shape.Extent.XMin)
        xmax = str(shape.Extent.XMax)
        ymin = str(shape.Extent.YMin)
        ymax = str(shape.Extent.YMax)
    except:
        # If an error is thrown, save message and return
        return -1, 'Problem obtaining spatial information from file. '

    # If sucessful, return bounding box
    return 1, xmin + " " + ymin + " " + xmax + " " + ymax  # return the string in the specific order defined above