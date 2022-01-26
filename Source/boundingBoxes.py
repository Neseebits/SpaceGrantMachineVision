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
import logger
import exceptions


# gets the coordinates out of the bounding box list/array
def getBoundingBoxCords(box):
    return int(box[0][0]), int(box[0][1]), int(box[1][0]), int(box[1][1])

# makes points out of the bounding box coordinates
def getBoundingBoxPoints(box):
    x1, y1, x2, y2 = getBoundingBoxCords(box)
    return (x1, y1), (x2, y1), (x2, y2), (x1, y2)

# image is a cv2 image, which is a numpy array
# boundingBoxes is as follows
#        [ [x1, y1], [x2, y2] ]
#        where x1, y1, x2, y2 are any number
# the number type gets sanitized upon boundingBox load coordinates
def drawBoundingBoxes(rawImage, boundingBoxes, color=(0,0,255), thickness=2, windowName="Bounding Boxes"):
    image = np.copy(rawImage)
    for box in boundingBoxes:
        p1, p2, p3, p4 = getBoundingBoxPoints(box)
        cv2.line(image, p1, p2, color, thickness)
        cv2.line(image, p2, p3, color, thickness)
        cv2.line(image, p3, p4, color, thickness)
        cv2.line(image, p4, p1, color, thickness)
        cv2.imshow(windowName, image)