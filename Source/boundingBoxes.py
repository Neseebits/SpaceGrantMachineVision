# Built in python libs
import os
import sys
import time
import math

# Additional libs
import numpy as np
import cv2
from numba import jit, njit

# Custom  imports
try:
    from logger import Logger
    import exceptions
    from cameras.DisplayManager import DisplayManager
except ImportError:
    from Source.logger import Logger
    from Source import exceptions
    from Source.cameras.DisplayManager import DisplayManager


# gets the coordinates out of the bounding box list/array
def getBoundingBoxCords(box):
    return int(box[0][0]), int(box[0][1]), int(box[1][0]), int(box[1][1])

# makes points out of the bounding box coordinates
def getBoundingBoxPoints(box):
    x1, y1, x2, y2 = getBoundingBoxCords(box)
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

# image is a cv2 image, which is a numpy array
# boundingBoxes is as follows
#        [ [x1, y1], [x2, y2] ]
#        where x1, y1, x2, y2 are any number
# the number type gets sanitized upon boundingBox load coordinates
def drawBoundingBoxes(rawImage, boundingBoxes, color=(0,0,255), thickness=2, windowName="Bounding Boxes", show=False):
    image = np.copy(rawImage)
    for box in boundingBoxes:
        [p1, p2, p3, p4] = getBoundingBoxPoints(box)
        cv2.rectangle(image, p1, p3, color, thickness)
    if show:
        # DisplayManager.show(windowName, image)
        cv2.imshow(windowName, image)
    return image

# determine a connection between two bounding boxes
def determineConnection(box1, box2, connectedness):
    pts1 = getBoundingBoxPoints(box1)
    pts2 = getBoundingBoxPoints(box2)
    if connectedness == 4:
        # check that any of the two sides are shared
        # append the first point to the end for checking the last side
        pts1.append(pts1[0])
        pts2.append(pts2[0])
        # cycle over each point in points 1 then cycle over each point in
        for i in range(len(pts1) - 1):
            for j in range(len(pts2) - 1):
                if pts1[i] == pts2[j] and pts1[i+1] == pts2[j+1]:
                    return True
        return False
    elif connectedness == 8:
        # check if any point is the same
        for pt1 in pts1:
            for pt2 in pts2:
                if pt1 == pt2:
                    return True
        return False
    else:
        raise exceptions.ConnectednessError(connectedness)

# functions that given bounding box data combines connected bounding boxes
def combineBoundingBoxes(boundingBoxes, connectedness=4):
    if len(boundingBoxes) <= 1:
        return boundingBoxes
    return boundingBoxes

