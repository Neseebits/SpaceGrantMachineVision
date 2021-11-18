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
    gotLeft, leftImage = cameras[0].read()
    gotRight, rightImage = cameras[1].read()
    # Ensure images were received
    if(not gotLeft): raise exceptions.CameraReadError("Left")
    if(not gotRight): raise exceptions.CameraReadError("Right")
    # Return images in tuple format
    return (leftImage, rightImage)

# Function makes a window which displays both camera feeds next to each other
# Takes the images as a tuple where the first,second correspond to left,right
# Has no return value, BUT requires a cv2.waitKey() after its call (bottom of loop)
def showCameras(images):
    if(images[0].shape != images[1].shape):
        minHeight = min(images[0].shape[0], images[1].shape[0])
        minWidth = min(images[0].shape[1], images[1].shape[1])
        newDim = (minWidth, minHeight)
        resizedImages = (cv2.resize(images[0], newDim), cv2.resize(images[1], newDim))
        cv2.imshow("Combined camera output", np.concatenate((resizedImages[0], resizedImages[1]), axis=1))
    else:
        cv2.imshow("Combined camera output", np.concatenate((images[0], images[1]), axis=1))

# Convenience function which will read and show the images given by readCameras and showCameras
# Will not pass the exception given by readCameras if a camera is not read
def readAndShowCameras(cameras):
    images = readCameras(cameras)
    showCameras(images)
    return images