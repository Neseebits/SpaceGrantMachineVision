# Built in python libs
import os
import sys
import time

# Additional libs
import numpy as np
import cv2

# Custom  imports
import exceptions

# Function to get the new frames from both cameras
# "Safe" such that it will throw an exception if the cameras do not yield frames
# Takes a tuple of camera numbers
# Returns a tuple of images
# Left image in return tuple corresponds to left camera number in return tuple
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

# Function makes a window which displays both camera feeds next to each other
# Takes the images as a tuple where the first,second correspond to left,right
# Has no return value, BUT requires a cv2.waitKey() at end of its call
def showCameras(images):
    if(images[0].shape != images[1].shape):
        minHeight = min(images[0].shape[0], images[1].shape[0])
        minWidth = min(images[0].shape[1], images[1].shape[1])
        newDim = (minWidth, minHeight)
        resizedImages = (cv2.resize(images[0], newDim), cv2.resize(images[1], newDim))
        cv2.imshow("Combined camera output", np.concatenate((resizedImages[0], resizedImages[1]), axis=1))
    else:
        cv2.imshow("Combined camera output", np.concatenate((images[0], images[1]), axis=1))
    # cv2.waitKey is needed for opencv to properly display images (think of it like a timer or interrupt)
    key_pressed = cv2.waitKey(10) & 0xFF
    if key_pressed == 27:
        raise exceptions.KeyboardInterrupt("ESC")  # Quit on ESC

# Convenience function which will read and show the images given by readCameras and showCameras
# Will pass on exceptions
def readAndShowCameras(cameras):
    try:
        images = readCameras(cameras)
        showCameras(images)
        return images
    except Exception as e:
        raise e