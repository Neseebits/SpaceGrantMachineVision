# Built in python libs
import os
import sys
import time
import pathlib

# Additional libs
import numpy as np
import cv2
from numba import jit
from multiprocessing import Lock

# Custom imports
from logger import Logger
import exceptions
from cameras import writeKandDistNPZ, initCameras, fetchAndShowCameras, loadUndistortionFiles
from visualOdometry.visualodometry import computeDisparity
from features import computeMatchingPoints, getPointsFromKeypoints
from objectDetection.featureDensity import findFeatureDenseBoundingBoxes
from utility import getAvgTimeArr

# Primary function where our main control flow will happen
# Contains a while true loop for continous iteration
def main():
    HEADLESS = False

    numTotalIterations = 0
    consecutiveErrors = 0
    iterationCounter = 0
    iterationTimes = []
    cameraFrameTimes = []
    featureFrameTimes = []
    featureDenseFrameTimes = []
    leftImage, rightImage, grayLeftImage, grayRightImage = None, None, None, None
    leftPts, rightPts, leftKp, leftDesc, rightKp, rightDesc = None, None, None, None, None, None
    featureDenseBoundingBoxes = None
    while True:
        iterationStartTime = time.time()
        try:
            # need to save previous images (if they exist) for visual odometry
            prevLeftImage, prevRightImage = leftImage, rightImage
            prevGrayLeftImage, prevGrayRightImage = grayLeftImage, grayRightImage

            # save previous feature information
            prevLeftPts, prevRightPts = leftPts, rightPts
            prevLeftKp, prevRightKp = leftKp, rightKp
            prevLeftDesc, prevRightDesc = leftDesc, rightDesc
            prevFeatureDenseBoundingBoxes = featureDenseBoundingBoxes

            cameraStartTime = time.time()
            # Satisfies that read images stage of control flow
            leftImage, rightImage, grayLeftImage, grayRightImage = fetchAndShowCameras(cameraPath, cameraLock, show=not HEADLESS)
            cameraFrameTimes.append(time.time() - cameraStartTime)

            featureStartTime = time.time()
            # feature points for left and right images
            # the point at index [0], [1], [2], etc. in both is the same real life feature,
            leftPts, rightPts, leftKp, leftDesc, rightKp, rightDesc = computeMatchingPoints(grayLeftImage,
                                                                                            grayRightImage, orb,
                                                                                            matcher, show=not HEADLESS)
            featureFrameTimes.append(time.time() - featureStartTime)

            featureDenseStartTime = time.time()
            # acquires the bounding box cordinates for areas of the image where there are dense features
            featureDenseBoundingBoxes = findFeatureDenseBoundingBoxes(leftImage, getPointsFromKeypoints(leftKp),
                                                                      binSize=30.0, featuresPerPixel=0.04, show=not HEADLESS)
            featureDenseFrameTimes.append(time.time() - featureDenseStartTime)

            # all additional functionality should be present within the === comments
            # additional data that needs to be stored for each iteration should be handled above
            #===========================================================================================================
            if numTotalIterations > 1:

                # this disparity map calculation should maybe get removed since we ??only?? care about the depth values
                disparityMap = computeDisparity(stereo, grayLeftImage, grayRightImage, show=not HEADLESS)

                # TODO
                # Fill in remainder of functionality

            #===========================================================================================================
            # Resets the consecutive error count if a full iteration is completed
            consecutiveErrors = 0
            # cv2.waitKey is needed for opencv to properly display images (think of it like a timer or interrupt)
            keyPressed = cv2.waitKey(10) & 0xFF
            if keyPressed == 27:
                raise exceptions.KeyboardInterrupt("ESC")  # Quit on ESC
        except exceptions.KeyboardInterrupt as e:  # Kills the loop if a keyboardInterrupt occurs
            Logger.log("User killed loop with: " + e.getKey())
            break
        except Exception as e:
            # Possibly instead of restarting, we might want to look into
            Logger.log(
                str(e) + " -> Occured in primary operation loop of program. Failed iterations in a row: {}".format(
                    consecutiveErrors))
            consecutiveErrors += 1
            if (consecutiveErrors > errorTolerance):
                Logger.log("RESTARTING PRIMARY CONTROL LOOP")
                break
        if iterationCounter < iterationsToAverage:
            iterationTimes.append(time.time() - iterationStartTime)
            iterationCounter += 1
        else:
            iterNum = "#{} Total Iterations: ".format(numTotalIterations + 1)
            iterTimeStr = "Avg iteration: {} {}".format(getAvgTimeArr(iterationTimes, iterationCounter), "ms")
            cameraTimeStr = " => Avg frame: {} {}".format(getAvgTimeArr(cameraFrameTimes, iterationCounter), 'ms')
            featureTimeStr = ", Avg features: {} {}".format(getAvgTimeArr(featureFrameTimes, iterationCounter), 'ms')
            objectDectTimeStr = ", Avg feature density: {} {}".format(getAvgTimeArr(featureDenseFrameTimes,
                                                                                    iterationCounter), 'ms')
            Logger.log(iterNum + iterTimeStr + cameraTimeStr + featureTimeStr + objectDectTimeStr)
            iterationCounter = 0
            iterationTimes = []
            cameraFrameTimes = []
            featureFrameTimes = []
            featureDenseFrameTimes = []
        numTotalIterations += 1


# Function that will run some code one time before anything else
# Primarily used for creating some files and/or testing some code
def optional():
    Logger.log("Running any optional code")
    lk = np.asarray([[10,0,320],[0,10,240],[0,0,1]])
    ld = np.asarray([[0],[0],[0],[0]])
    rk = lk
    rd = ld
    writeKandDistNPZ(lk, rk, ld, rd)

    Logger.log("Finished running any optional code")

if __name__ == "__main__":
    Logger.init("log.log")  # Starts the logger and sets the logger to log to the specified file.
    #optional()
    # Global constants for any hyperparameters for the code or physical constants
    # Define any global constants
    errorTolerance = 2  # defines the amount of skipped/incomplete iterations before the loop is restarted
    iterationsToAverage = 9  # use n+1 to calculate true number averaged

    # defining opencv objects
    orb = cv2.ORB_create(nfeatures=1000)  # orb feature detector object
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)  # matcher object
    stereo = cv2.StereoSGBM_create()  # stereo object

    # loading data for cameras and starting the camera process
    leftCamera = cv2.CAP_DSHOW + 0  # cv2.CAP_DSHOW changes internal api stuff for opencv
    rightCamera = cv2.CAP_DSHOW + 1  # add/remove cv2.CAP_DSHOW as needed for your system
    # Sets the exposure of the cameras. This process is finicky on what values are entered.
    # leftCamera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1.0)
    # leftCamera.set(cv2.CAP_PROP_EXPOSURE, 100.0)
    # Logger.log("Left exposure: " + str(leftCamera.get(cv2.CAP_PROP_EXPOSURE)))
    # rightCamera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1.0)
    # rightCamera.set(cv2.CAP_PROP_EXPOSURE, 100.0)
    # Logger.log("Right exposure: " + str(rightCamera.get(cv2.CAP_PROP_EXPOSURE)))
    cameraPath = "Data/Cameras/"
    if not os.path.isdir(cameraPath):
        cameraPath = "../" + cameraPath + "/"
    leftK, rightK, leftDistC, rightDistC = loadUndistortionFiles()
    cameraLock = Lock()
    initCameras(cameraPath, leftCamera, rightCamera, leftK, rightK, leftDistC, rightDistC, cameraLock)

    Logger.log("SYSTEM INFORMATION:")
    # TODO
    # print/log any nessecary system information
    Logger.log("Program starting...")
    while True:
        Logger.log("Starting loop...")
        main()
        Logger.log("Shutdown loop...")
        # sleep and then check for keyboardInterupt will fully kill program
        time.sleep(2)
        keyPressed = cv2.waitKey(10) & 0xFF
        if keyPressed == 27:
            Logger.log("Program shutdown...")
            break

    cv2.destroyAllWindows()
    Logger.shutdown()  # Shuts down the logging system and prints a closing message to the file
    sys.exit(0)
