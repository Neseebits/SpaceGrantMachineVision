# Built in python libs
import os
import sys
import time

# Additional libs
import numpy as np
import cv2

# Custom imports
import exceptions
from logger import Logger

# get the height and width dimensions from an image
def getHeightWidth(img):
    return img.shape[0], img.shape[1]

# UNTESTED
# read all images in given folder, if recurse is true will also get all images in sub_folders of the given folder
# prints an error if cv2.imread() throws an exception
# it is valid for there to be non image files in the directories, this will ignore those
def readImagesFromFolder(folder, recurse):
    # Raise any exception that isn't for the images, otherwise 'undefined' behavior
    try:
        allImages = [] # List to store OpenCV images in (OpenCV images are np arrays)
        for root, dirs, files in os.walk(folder): # os.walk finds everything in a given directory
            for file in files: # only care about files for loading images
                # try/except for opening images, because there could be files we don't want in there, but still want the images
                try: 
                    image = cv2.imread(file)
                    if image is not None:
                        allImages.append(image)
                except: 
                    Logger.log("Attempted to open file: {}".format(file))
            # If the want to get images recursively
            if recurse:
                for dir in dirs: # Loop over all directorys in the given directory and perform the same function
                    # add additional images found to same return list
                    pathToFolder = os.path.join(folder, dir)
                    recursiveImages = readImagesFromFolder(pathToFolder, recurse)
                    allImages = allImages + recursiveImages
        return allImages
    except Exception as e:
        raise e
# UNTESTED