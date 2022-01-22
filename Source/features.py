# Built in python libs
import os
import sys
import time

# Additional libs
import numpy as np
import cv2
from numba import jit

# Custom  imports
from logger import Logger
import exceptions
import utility


# function that given to images computes their features
# this does not do any filtering
# takes two grayscale images and a cv2 feature detector
def getImagePairKeyDesc(left, right, featureDetector):
    kp1, des1 = featureDetector.detectAndCompute(left, None)
    kp2, des2 = featureDetector.detectAndCompute(right, None)
    return kp1, des1, kp2, des2

# get features for a single image
# this does not do any filtering
# takes a single greyscale image
def getImageKeyDesc(image, featureDetector):
    try:
        return featureDetector.detectAndCompute(image, None)
    except:
        raise exceptions.FeatureMatchingError("Error running detect and compute in GetImageKeyDesc")

# get point cordinates from a list of keypoints
def getPointsFromKeypoints(kp):
    try:
        return cv2.KeyPoint_convert(kp)
    except:
        raise exceptions.FeatureMatchingError("Error converting array cv2.KeyPoint to array of array points")


# TODO
# add comments

# funtion that computes the matching features between two images and returns the corresponding points
# takes two grayscale images, a feature detector, and a matcher
def computeMatchingPoints(left, right, featureDetector, featureMatcher, ratio=3.0, showMatches=False, verbose=False):
    if verbose:
        Logger.log("Starting features.computeMatchingPoints")
    try:
        leftKp, leftDesc, rightKp, rightDesc = getImagePairKeyDesc(left, right, featureDetector)
        matches = featureMatcher.match(leftDesc, rightDesc)
        sortedMatches = np.array(sorted(matches, key=lambda x: x.distance))
        try:
            minDist = sortedMatches[0].distance
        except Exception as e:
            Logger.log(e)
            raise exceptions.FeatureMatchingError("No valid feature matches on raw feature keypoints")
        # perform ratio test on matching keypoints
        goodDistanceDiffs = []
        for m in matches:
            if m.distance < ratio * minDist:
                goodDistanceDiffs.append(m)
        ratioMatches = sorted(goodDistanceDiffs, key=lambda x: x.distance)
        if len(ratioMatches) == 0:
            raise exceptions.FeatureMatchingError("No valid features generated after performing ratio test")
        try:
            # (x, y) coordinates from the first image.
            left_pts = np.array(np.float32([leftKp[m.trainIdx].pt for m in ratioMatches]).reshape(-1, 1, 2))
            # (x, y) coordinates from the second image.
            right_pts = np.array(np.float32([rightKp[m.trainIdx].pt for m in ratioMatches]).reshape(-1, 1, 2))
        except Exception as e:
            Logger.log(e)
            raise exceptions.FeatureMatchingError("Error extracting points from matched features")
        if showMatches:
            matchedImg = cv2.drawMatches(left, left_pts, right, right_pts, ratioMatches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            cv2.imshow("Matched Features", matchedImg)
        return left_pts, right_pts
    except Exception as e: # generic exception catcher, just return no list of points
        Logger.log(e)
        return [], []
