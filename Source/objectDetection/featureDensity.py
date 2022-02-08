# Built in python libs
import math

# Additional libs
import numpy as np
from numba import jit

# Custom  imports
try:
    from logger import Logger
    import exceptions
    from features import getPointsFromKeypoints, getImageKeyDesc, getImagePairKeyDesc
    from boundingBoxes import drawBoundingBoxes, combineBoundingBoxes
    from cameras.DisplayManager import DisplayManager
except ImportError:
    from Source.logger.logger import Logger
    from Source.utilities import exceptions
    from Source.features import getPointsFromKeypoints, getImageKeyDesc, getImagePairKeyDesc
    from Source.utilities.boundingBoxes import drawBoundingBoxes, combineBoundingBoxes
    from Source.cameras.DisplayManager import DisplayManager

# given a point in x, y cordinates, an image, and an array of keypoints
# determines if the surrounding region contains enough pixel of density
# returns Boolean, x1, y1, x2, y2
# where x1, y1, x2, y2 are the top left and bottom right image cordinates
# if the boolean is False the points are all -1
@jit(nopython=True)
def isFeatureDense(x, y, iwidth, iheight, kp, width, height, featurePerPixel):
    # check if x and y are inside of the image
    # determine the top left and bottom right bounding box cordinates for the region
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
    # print(f"topBound:{topBound}, bottomBound:{bottomBound}, leftBound{leftBound}, rightBound{rightBound}")
    kpInRegion = 0.0
    for keypoint in kp:
        kx = keypoint[0]
        ky = keypoint[1]
        if (leftBound < kx < rightBound) and (topBound < ky < bottomBound):
            kpInRegion += 1.0
            # print(f"Keypoint x:{kx} y:{ky}")
    density = kpInRegion / float(width * height)
    # print(f"Density: {density}, kpInRegion: {kpInRegion}\n")
    if density >= featurePerPixel:
        return True, leftBound, topBound, rightBound, bottomBound
    else:
        return False, -1, -1, -1, -1


# iterates over every bin in the image and determines if that bin is feature dense
# if the bin is feature dense, it will save its bounding box
@jit(nopython=True)
def getFeatureDenseBoundingBoxes(imageWidth, imageHeight, pts, horzBins, vertBins, binSize, featuresPerPixel):
    # bounding boxes are stored as [[x1, y1], [x2, y2]]
    boundingBoxes = []
    for i in range(horzBins):
        for j in range(vertBins):
            x = i * binSize + 0.5 * binSize
            y = j * binSize + 0.5 * binSize
            dense, x1, y1, x2, y2 = isFeatureDense(x, y, imageWidth, imageHeight, pts, binSize, binSize,
                                                   featuresPerPixel)
            if dense:
                boundingBoxes.append(np.array([[x1, y1], [x2, y2]]))
    return boundingBoxes

# takes an image and returns bounding box coordinates
def findFeatureDenseBoundingBoxes(image, pts, binSize=30.0, featuresPerPixel=0.01, show=False, threadedDisplay=True):
    # compute dimensional information
    imageHeight, imageWidth = image.shape[0], image.shape[1]
    horzBins, vertBins = math.ceil(imageWidth / binSize), math.ceil(imageHeight / binSize)

    # compute the bounding boxes where there are features exceeding a threshold
    boundingBoxes = getFeatureDenseBoundingBoxes(imageWidth, imageHeight, pts, horzBins, vertBins, binSize,
                                                 featuresPerPixel)

    # simplifiedBoundingBoxes = combineBoundingBoxes(boundingBoxes)

    if show:
        drawBoundingBoxes(image, boundingBoxes, windowName="Feature Dense Bounding Boxes", show=True, threadedDisplay=threadedDisplay)
        # drawBoundingBoxes(image, simplifiedBoundingBoxes, windowName="Simplified FeatureDense BB", show=True)

    return boundingBoxes