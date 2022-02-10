#********************************************
# This file is step two of two to clip a large number of raster files.
# This file will preform the clipping operations on the provided rasters
# to the specifications in the JSON files. Multiple JSON files can be
# processed at the same time.
#
# NOTE TO GRADERS: It can take a while to process large rasters like the
#                  ones used in this project. If you want to test the
#                  functionality of these programs, I would suggest using
#                  a small area.
#
# This code written by Kaden Flick
# GEOG 462 - Spring 2021
#********************************************

import tkinter as tk
import tkinter.filedialog as tkfd
import supporting_functions as sf

def main ():
    # Set up tkinter window
    window = tk.Tk()
    window.attributes('-topmost', True)
    window.lift()
    window.withdraw()

    # Get JSON files to process from user
    print("Select JSON files to be processed. Hold control to select multiple files.")
    list_filetypes = (("JSON files","*.json"), ("All files","*.*"))
    json_files = tkfd.askopenfilenames(parent = window, initialdir = 'JSON files', title = 'Select JSON Files', filetypes = list_filetypes)

    # Destroy tkinter window
    window.destroy()

    # Create list of files and create list of dictionaries
    json_files = list(json_files)
    list_param_dict = [sf.parse_json(item) for item in json_files]

    # Iterate through the dictionaries
    for x in range(0, len(list_param_dict)):
        print('\n')

        # Execute bulk clipping using paramters in current dictionary
        success, message = sf.bulk_clipping(list_param_dict[x])

        # Print messages returned by bulk clipping
        if success == 1:
            print("Sucessfully completed processing for {}".format(json_files[x]))
            print("Output stored at {}".format(list_param_dict[x]['output_directory']))
        elif success != 1:
            print("Did not successfully complete processing for {}".format(json_files[x]))
            print("Error message: {}".format(message))

    # Get input from user to close program
    input("\nPress Enter to quit...")
    return 1

if __name__ == '__main__':
    main()