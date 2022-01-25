# Built in python libs
import os
import sys
import time

# Additional libs
import numpy as np
import cv2
from numba import jit, njit

# Custom  imports
from Source.logger import Logger
from Source import exceptions
from Source import utility
from Source.features import getPointsFromKeypoints, getImageKeyDesc, getImagePairKeyDesc


# given a point in x, y cordinates, an image, and an array of keypoints
# determines if the surrounding region contains enough pixel of density
# returns Boolean, x1, y1, x2, y2
# where x1, y1, x2, y2 are the top left and bottom right image cordinates
# if the boolean is False the points are all -1
def isFeatureDense(x, y, image, kp, featurePerPixel=0.1, width=30, height=30):
    # check if x and y are inside of the image
    # determine the top left and bottom right bounding box cordinates for the region
    iheight, iwidth = utility.getHeightWidth(image)
    leftBound = x - width / 2
    rightBound = x + width / 2
    if leftBound < 0:
        leftBound = 0
    if rightBound >= iwidth:
        rightBound = iwidth - 1
    topBound = y - height / 2
    bottomBound = y + height / 2
    if topBound < 0:
        topBound = 0
    if bottomBound >= iheight:
        bottomBound = iheight - 1
    # iterate over keypoints, determine if within boundary
    kpInRegion = 0
    for keypoint in kp:
        kx = keypoint[0]
        ky = keypoint[1]
        if (leftBound < kx < rightBound) and (topBound < ky < bottomBound):
            kpInRegion += 1
    density = kpInRegion / (width * height)
    if density >= featurePerPixel:
        return True, leftBound, topBound, rightBound, bottomBound
    else:
        return False, -1, -1, -1, -1

# takes an image and returns bounding box cordinates
def findFeatureDensity(image, featureDetector, showRegions=False, verbose=False):
    kp, des = getImageKeyDesc(image, featureDetector)
    pts = getPointsFromKeypoints(kp)
    # TODO
    # Given the set of points 'bin' the image into regions and compute the number of points in each region
    # If a given region satisfies the given density of features / pixel than the region is determined to be of interest
    # The function will then return the bounding box cordinates for those regions of interest

