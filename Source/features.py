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

# get features for a single image
# this does not do any filtering
# takes a single greyscale image
def getImageKeyDesc(image, featureDetector):
    return featureDetector.detectAndCompute(image, None)

# get point cordinates from a list of keypoints
def getPointsFromKeypoints(kp):
    return cv2.KeyPoint_convert(kp)

# takes an image and returns bounding box cordinates
def findFeatureDensity(image, featureDetector):
    kp, des = getImageKeyDesc(image, featureDetector)
    pts = getPointsFromKeypoints(kp)



# TODO
# add comments

# funtion that computes the matching features between two images and returns the corresponding points
# takes two grayscale images, a feature detector, and a matcher
def computeMatchingPoints(left, right, featureDetector, featureMatcher, ratio=3.0, showMatches=False):
    try:
        leftKp, leftDesc, rightKp, rightDesc = getKeypointsDescriptors(left, right, featureDetector)
        matches = featureMatcher.match(leftDesc, rightDesc)
        sortedMatches = np.array(sorted(matches, key=lambda x: x.distance))
        try:
            minDist = sortedMatches[0].distance
        except:
            raise exceptions.FeatureMatchingError()
        goodDistanceDiffs = []
        for m in matches:
            if m.distance < ratio * minDist:
                goodDistanceDiffs.append(m)
        ratioMatches = sorted(goodDistanceDiffs, key=lambda x: x.distance)
        # (x, y) coordinates from the first image.
        left_pts = np.array(np.float32([leftKp[m.trainIdx].pt for m in ratioMatches]).reshape(-1, 1, 2))
        # (x, y) coordinates from the second image.
        right_pts = np.array(np.float32([rightKp[m.trainIdx].pt for m in ratioMatches]).reshape(-1, 1, 2))
        if showMatches:
            matchedImg = cv2.drawMatches(left, left_pts, right, right_pts, ratioMatches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            cv2.imshow("Matched Features", matchedImg)
        return left_pts, right_pts
    except exceptions.FeatureMatchingError as e:
        raise exceptions.FeatureMatchingError()
    except: # who knows what happens to get here
        return [], []
