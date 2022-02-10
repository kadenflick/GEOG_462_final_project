#********************************************
# This file is step one of two to clip a large number of raster files.
# This file will walk the user through inputing information about the
# desired rasters to be clipped and then save all of that information
# in a JSON file to be read later.
#
# NOTE TO GRADERS: It can take a while to process large rasters like the
#                  ones used in this project. If you want to test the
#                  functionality of these programs, I would suggest using
#                  a small area.
#
# This code written by Kaden Flick
# GEOG 462 - Spring 2021
#********************************************

import json, os.path
import supporting_functions as sf

def main ():
    print("This program will create a json file for bulk clipping of rasters.\n")

    while True:
        # Set up defualt dictionary - this is here to make changing defaults easier if required
        default_dict = {
            'raster_files': (),
            'polygon_files': (),
            'output_directory': '*',
            'output_extentsion': '.tif',
            'nodata_value': '0',
            'maintain_clipping_extent': 'MAINTAIN_EXTENT',
        }

        # Get inputs from user and save to dictionary
        user_dict, filename = sf.get_user_info(default_dict)

        # If 'JSON files' directory doesn't exist, create it
        if not os.path.exists('JSON files'):
            os.mkdir('JSON files')

        # Write to JSON file
        filepath_complete = r'JSON Files\{}.json'.format(filename)

        counter = 1
        recheck = False

        # Make sure that the filename provided by the user doesn't exist. Fix if it does
        while True:
            if os.path.isfile(filepath_complete):
                # If the file exists, rename it
                if not recheck:
                    print("\n{} already exists. Fixing...".format(filepath_complete))

                    # This case is for the first instance of a file existing: file.json -> file(1).json
                    filepath_complete = r'{}({}){}'.format(filepath_complete[:-5], counter, filepath_complete[-5:])
                else:
                    # This case is for if multiple copies of a file existing: file(x).json -> file(x + 1).json
                    filepath_complete = r'{}{}{}'.format(filepath_complete[:-7], counter, filepath_complete[-6:])

                counter = counter + 1
                recheck = True
            else:
                break

        # Save information to a JSON file in a human readable format
        with open(filepath_complete, 'w') as outfile:
            json.dump(user_dict, outfile, indent = 4)

        print("\nParameters for '{}' have been stored in '{}'\n".format(filename, filepath_complete))

        # Ask if user wants to create a new batch
        print("Create new batch? [Y/N]")
        quit_prog = sf.check_yes_no()

        # If not, quit
        if quit_prog == 'n' or quit_prog == 'N':
            print("\nExiting... ")
            break
        else:
            print("\n")

    return 1

if __name__ == '__main__':
    main()