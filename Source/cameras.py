# Built in python libs
import os
import sys
import time

# Additional libs
import numpy as np
import cv2
from numba import jit

# Custom  imports
import exceptions

# TODO
# Switch to using grab and decode in two lines, but grabbing both cameras at once and decoding both at once
# Switch to using Numba for JIT compilation

# Function to get the new frames from both cameras
# "Safe" such that it will throw an exception if the cameras do not yield frames
# Takes a tuple of camera numbers
# Returns a tuple of images
# Left image in return tuple corresponds to left camera number in return tuple
@jit(target='cpu', nopython=True)
def readCameras(cameras):
    # Got image boolean and retrieved image
    gotLeft = cameras[0].grab()
    gotRight = cameras[1].grab()
    # Ensure images were received
    if not gotLeft:
        raise exceptions.CameraReadError("Left")
    if not gotRight:
        raise exceptions.CameraReadError("Right")
    # Return images in tuple format
    return (cameras[0].retrieve(), cameras[1].retrieve())

# TODO
# Switch to using Numba for JIT compilation

# Function makes a window which displays both camera feeds next to each other
# Takes the images as a tuple where the first,second correspond to left,right
# Has no return value, BUT requires a cv2.waitKey() at end of overall loop
def showCameras(images):
    if(images[0].shape != images[1].shape):
        minHeight = min(images[0].shape[0], images[1].shape[0])
        minWidth = min(images[0].shape[1], images[1].shape[1])
        newDim = (minWidth, minHeight)
        resizedImages = (cv2.resize(images[0], newDim), cv2.resize(images[1], newDim))
        cv2.imshow("Combined camera output", np.concatenate((resizedImages[0], resizedImages[1]), axis=1))
    else:
        cv2.imshow("Combined camera output", np.concatenate((images[0], images[1]), axis=1))

# TODO
# Switch to using Numba for JIT compilation

# Convenience function which will read and show the images given by readCameras and showCameras
# Will pass on exceptions
def readAndShowCameras(cameras):
    try:
        images = readCameras(cameras)
        showCameras(images)
        return images
    except Exception as e:
        raise e