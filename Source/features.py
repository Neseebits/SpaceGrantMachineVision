# Built in python libs

# Additional libs
import numpy as np
import cv2
from numba import jit

# Custom  imports
try:
    from logger.logger import Logger
    from utilities import exceptions
    from cameras.DisplayManager import DisplayManager
except ImportError:
    from Source.logger.logger import Logger
    from Source import exceptions
    from Source.cameras.DisplayManager import DisplayManager

# function that given to images computes their features
# this does not do any filtering
# takes two grayscale images and a cv2 feature detector
# @jit(forceobj=True)
def getImagePairKeyDesc(left, right, featureDetector):
    kp1, des1 = getImageKeyDesc(left, featureDetector)
    kp2, des2 = getImageKeyDesc(right, featureDetector)
    return kp1, des1, kp2, des2

# get features for a single image
# this does not do any filtering
# takes a single greyscale image
# @jit(forceobj=True)
def getImageKeyDesc(image, featureDetector):
    return featureDetector.detectAndCompute(image, None)

# get point cordinates from a list of keypoints
def getPointsFromKeypoints(kp):
    return cv2.KeyPoint_convert(kp)

# sorts matched keypoints returned directly from the cv2.matcher object
# this sorts them by distance
def sortMatches(matches):
    return np.array(sorted(matches, key=lambda x: x.distance))

# gets the image cordinates out of the matched keypoints
@jit(forceobj=True)
def getPointsFromMatches(matches, leftKp, rightKp):
    return [leftKp[mat.queryIdx].pt for mat in matches], [rightKp[mat.trainIdx].pt for mat in matches]

# performs the ratio test on a set of matched keypoints
# the ratio test filters matched keypoints out if they are greater than the minimum seperation between matched
# by a set amount. The usual value is 3. Thus, if the distance between two matched features is 3 times larger than the
# minimum pixel distance between 2 matched features, than we can say it is invalid and in outlier.
# This is because the typical image to image comparision will have a small change between frames
# takes a list of keypoints, a minimum distance, and a given ratio
# kpMatches must be SORTED for optimization purposes
def ratioTest(kpMatches, ratio):
    try:
        minDist = kpMatches[0].distance
    except:
        raise exceptions.FeatureMatchingError("ratioTest: No matched feature points present in kpMatches")
    goodDistanceDiffs = []
    for m in kpMatches:
        if m.distance < ratio * minDist:
            goodDistanceDiffs.append(m)
        else:
            break
    return goodDistanceDiffs

# funtion that computes the matching features between two images and returns the corresponding points
# takes two grayscale images, a feature detector, and a matcher
# the showMatches optional parameter shows the total features and not the ones acquired through the ratio test
def computeMatchingPoints(left, right, featureDetector, featureMatcher, ratio=3.5, show=False, threadedDisplay=True):
    try:
        leftKp, leftDesc, rightKp, rightDesc = getImagePairKeyDesc(left, right, featureDetector)
        matches = featureMatcher.match(leftDesc, rightDesc)
        if len(matches) == 0:
            raise exceptions.FeatureMatchingError("computeMatchingPoints: No matched features present in the matched features ")
        # sort the matches
        sortedMatches = sortMatches(matches)
        # perform ratio test on matching keypoints
        ratioMatches = ratioTest(sortedMatches, ratio=ratio)
        if len(ratioMatches) == 0:
            ratioMatches = sortedMatches
        # extract image cordinates of matches
        try:
            left_pts, right_pts = getPointsFromMatches(ratioMatches, leftKp, rightKp)
        except:
            raise exceptions.FeatureMatchingError("computeMatchingPoints: Could not pull points from features")
        # show the output
        if show:
            try:
                matchedImg = cv2.drawMatches(left, leftKp, right, rightKp, ratioMatches, None, flags=2) #<- 7% compute time
                if threadedDisplay:
                    DisplayManager.show("Matched Features", matchedImg)
                else:
                    cv2.imshow("Matched Features", matchedImg)
            except:
                Logger.log("    computeMatchingPoints -> Failed to display matches")
        return left_pts, right_pts, leftKp, leftDesc, rightKp, rightDesc
    except Exception as e: # generic exception catcher, just return no list of points
        raise e
