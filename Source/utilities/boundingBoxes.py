# Built in python libs

# Additional libs
import numpy as np
import cv2
from numba import jit

# Custom  imports
try:
    from Source.logger.logger import Logger
    import exceptions
    from cameras.DisplayManager import DisplayManager
except ImportError:
    from Source.logger.logger import Logger
    from Source.utilities import exceptions
    from Source.cameras.DisplayManager import DisplayManager


# gets the coordinates out of the bounding box list/array
# bounding box must be a np.array
# np.array([[x1, y1], [x2, y2]])
@jit(nopython=True)
def getBoundingBoxCords(box):
    #      x1 [0]          y1 [1]          x2 [2]          y2 [3]
    return int(box[0][0]), int(box[0][1]), int(box[1][0]), int(box[1][1])

# makes points out of the bounding box coordinates
@jit(nopython=True)
def getBoundingBoxPoints(box):
    x1, y1, x2, y2 = getBoundingBoxCords(box)
    return np.array([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])

# image is a cv2 image, which is a numpy array
# boundingBoxes is as follows
#        [ [x1, y1], [x2, y2] ]
#        where x1, y1, x2, y2 are any number
# the number type gets sanitized upon boundingBox load coordinates
def drawBoundingBoxes(rawImage, boundingBoxes, color=(0,0,255), thickness=2, windowName="Bounding Boxes", show=False,
                      threadedDisplay=True):
    image = np.copy(rawImage)
    for box in boundingBoxes:
        [p1, p2, p3, p4] = getBoundingBoxPoints(box)
        if isinstance(p1, np.ndarray) or isinstance(p3, np.ndarray):
            p1, p3 = (p1[0], p1[1]), (p3[0], p3[1])
        cv2.rectangle(image, p1, p3, color, thickness)
    if show:
        if threadedDisplay:
            DisplayManager.show(windowName, image)
        else:
            cv2.imshow(windowName, image)
    return image

# checks each point in a boundingBox and determines they are equal if each point is equal
@jit(nopython=True)
def boundingBoxEquals(box1, box2):
    if not (box1[0][0] == box2[0][0] and box1[0][1] == box2[0][1] and
            box1[1][0] == box2[1][0] and box1[1][1] == box2[1][1]):
        return False
    return True

# determine if there is a connection between two bounding boxes
@jit(nopython=True)
def determineConnection(box1, box2, connectedness):
    pts1 = getBoundingBoxPoints(box1)
    pts2 = getBoundingBoxPoints(box2)
    if connectedness == 4:
        # check that any of the two sides are shared
        # append the first point to the end for checking the last side
        pts1 = np.append(pts1, pts1[0]) # pts1.append(pts1[0])
        pts2 = np.append(pts2, pts2[0]) # pts2.append(pts2[0])
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
                if pt1[0] == pt2[0] and pt1[1] == pt2[1]:
                    return True
        return False

# need a function to loop over boundingBoxes for the given bounding box, and determine if each one has a connection or not
# when a box has a connection, that boundingBox must also be iterated over.
@jit(nopython=True)
def findConnectedBoundingBoxes(startingBox, boundingBoxes, connectedness):
    connectedBoxes = np.array(startingBox)
    for box in connectedBoxes:
        for newBox in boundingBoxes:
            if not boundingBoxEquals(box, newBox) and determineConnection(box, newBox, connectedness):
                connectedBoxes = np.append(connectedBoxes, newBox)
    return connectedBoxes

# determines the new corners of the bounding box encapsulating two other bounding boxes
def determineMaxMinCorners(boundingBoxes):
    if len(boundingBoxes) == 1:
        return boundingBoxes[0]
    x1s = []
    y1s = []
    x2s = []
    y2s = []
    for box in boundingBoxes:
        x1, y1, x2, y2 = getBoundingBoxCords(box)
        x1s.append(x1)
        y1s.append(y1)
        x2s.append(x2)
        y2s.append(y2)
    minX = min(x1s)
    maxX = max(x2s)
    minY = min(y1s)
    maxY = max(y2s)
    # construct a new boundingBox
    return np.array([[minX, minY], [maxX, maxY]])

# functions that given bounding box data combines connected bounding boxes
# @jit(nopython=True)
def combineBoundingBoxes(boundingBoxes, connectedness=8):
    if len(boundingBoxes) <= 1:
        return boundingBoxes
    # copy first element to back for circular checking
    connectedBoxes = list()
    simplifiedBoxes = list()
    for i, box1 in enumerate(boundingBoxes):
        connectedBoxes.append(box1)
        for j, box2 in enumerate(boundingBoxes):
            if i == j:
                continue
            if determineConnection(box1, box2, connectedness):
                connectedBoxes.append(boundingBoxes.pop(j))
                # need to erase the box that is appended or else it is double counted
        simplifiedBoxes.append(determineMaxMinCorners(connectedBoxes))
        connectedBoxes = list()
    return simplifiedBoxes

