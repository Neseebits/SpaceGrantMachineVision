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


# function that given to images computes their features
# this does not do any filtering
# takes two grayscale images and a cv2 feature detector
def getKeypointsDescriptors(left, right, featureDetector):
    kp1, des1 = featureDetector.detectAndCompute(left, None)
    kp2, des2 = featureDetector.detectAndCompute(right, None)
    return kp1, des1, kp2, des2

# TODO
# add comments

# funtion that computes the matching features between two images and returns the corresponding points
# takes two grayscale images, a feature detector, and a matcher
def computeMatchingPoints(left, right, featureDetector, featureMatcher, ratio=3.0):
    leftKp, leftDesc, rightKp, rightDesc = getKeypointsDescriptors(left, right, featureDetector)
    matches = featureMatcher.match(leftDesc, rightDesc)
    sortedMatches = np.array(sorted(matches, key=lambda x: x.distance))
    minDist = sortedMatches[0].distance
    goodDistanceDiffs = []
    for m in matches:
        if m.distance < ratio * minDist:
            goodDistanceDiffs.append(m)
    ratioMatches = sorted(goodDistanceDiffs, key=lambda x: x.distance)
    # (x, y) coordinates from the first image.
    dst_pts = np.array(np.float32([leftKp[m.trainIdx].pt for m in ratioMatches]).reshape(-1, 1, 2))
    # (x, y) coordinates from the second image.
    src_pts = np.array(np.float32([rightKp[m.trainIdx].pt for m in ratioMatches]).reshape(-1, 1, 2))
    return dst_pts, src_pts