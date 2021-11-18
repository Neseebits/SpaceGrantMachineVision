# Built in python libs
import os
import sys
import time

# Additional libs
import numpy as np
import cv2

# Custom imports
import exceptions

# UNTESTED
# read all images in given folder, if recurse is true will also get all images in sub_folders of the given folder
# prints an error if cv2.imread() throws an exception
# it is valid for there to be non image files in the directories, this will ignore those
def read_images(folder, recurse):
    # Raise any exception that isn't for the images, otherwise 'undefined' behavior
    try:
        all_images = [] # List to store OpenCV images in (OpenCV images are np arrays)
        for root, dirs, files in os.walk(folder): # os.walk finds everything in a given directory
            for file in files: # only care about files for loading images
                # try/except for opening images, because there could be files we don't want in there, but still want the images
                try: 
                    image = cv2.imread(file)
                    if image is not None:
                        all_images.append(image)
                except: 
                    print("Attempted to open file: {}".format(file))
            # If the want to get images recursively
            if recurse:
                for dir in dirs: # Loop over all directorys in the given directory and perform the same function
                    # add additional images found to same return list
                    path_to_folder = os.path.join(folder, dir)
                    recursive_images = read_images(path_to_folder, recurse)
                    all_images = all_images + recursive_images
        return all_images
    except Exception as e:
        raise e
# UNTESTED