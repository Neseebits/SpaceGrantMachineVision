# Built in python libs
import os
import sys
import time
import pathlib

# Additional libs
import numpy as np
import cv2
import numba

# Custom imports
from logger import Logger
import exceptions
from cameras import readAndShowCameras, getGrayscaleImages
from visualOdometry.visualodometry import computeDisparity
from features import computeMatchingPoints


# Primary function where our main control flow will happen
# Contains a while true loop for continous iteration
def main():
    firstIteration = True
    consecutiveErrors = 0
    iterationCounter = 0
    iterationTimes = []
    cameraFrameTimes = []
    featureFrameTimes = []
    leftImage, rightImage, grayLeftImage, grayRightImage = None, None, None, None
    leftPts, rightPts, leftKp, leftDesc, rightKp, rightDesc = None, None, None, None, None, None
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

            cameraStartTime = time.time()
            # Satisfies that read images stage of control flow
            leftImage, rightImage = readAndShowCameras(leftCamera, rightCamera, leftK, rightK, leftDistC, rightDistC,
                                                       show=True)
            # grayscale images for feature detection
            grayLeftImage, grayRightImage = getGrayscaleImages(leftImage, rightImage)
            cameraFrameTimes.append(time.time() - cameraStartTime)

            featureStartTime = time.time()
            # feature points for left and right images
            # the point at index [0], [1], [2], etc. in both is the same real life feature,
            leftPts, rightPts, leftKp, leftDesc, rightKp, rightDesc = computeMatchingPoints(grayLeftImage,
                                                                                            grayRightImage, orb,
                                                                                            matcher, showMatches=True)
            featureFrameTimes.append(time.time() - featureStartTime)

            # all additional functionality should be present within the === comments
            # additional data that needs to be stored for each iteration should be handled above
            #===========================================================================================================
            if not firstIteration:

                # this disparity map calculation should maybe get removed since we ??only?? care about the depth values
                disparityMap = computeDisparity(stereo, grayLeftImage, grayRightImage, show=True)

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
            iterTimeStr = "Avg iteration: {} {}".format(round((sum(iterationTimes) / iterationCounter) * 1000, 1), "ms")
            cameraTimeStr = ", Avg frame: {} {}".format(round((sum(cameraFrameTimes) / iterationCounter) * 1000, 1), 'ms')
            featureTimeStr = ", Avg features: {} {}".format(round((sum(featureFrameTimes) / iterationCounter) * 1000, 1), 'ms')
            Logger.log(iterTimeStr + cameraTimeStr + featureTimeStr)
            iterationCounter = 0
            iterationTimes = []
            cameraFrameTimes = []
            featureFrameTimes = []
        firstIteration = False


# Function that will run some code one time before anything else
# Primarily used for creating some files and/or testing some code
def optional():
    print("Running any optional code")
    # lk = np.asarray([[10,0,320],[0,10,240],[0,0,1]])
    # ld = np.asarray([[0],[0],[0],[0]])
    # rk = lk
    # rd = ld
    # cameras.writeKandDistNPZ(lk, rk, ld, rd)

    print("Finished running any optional code")


def loadFiles():
    # one time file loading for the camera intrinsic matrices and undistortion coeff
    calibrationPath = "Data/Calibration/"
    if not os.path.isdir(calibrationPath):
        calibrationPath = "../" + calibrationPath
    leftK = np.load(calibrationPath + "leftK.npy")
    rightK = np.load(calibrationPath + "rightK.npy")
    leftDistC = np.load(calibrationPath + "leftDistC.npy")
    rightDistC = np.load(calibrationPath + "rightDistC.npy")

    return leftK, rightK, leftDistC, rightDistC


if __name__ == "__main__":
    optional()
    Logger.init("log.log")  # Starts the logger and sets the logger to log to the specified file.
    # Global constants for any hyperparameters for the code or physical constants
    # Define any global constants
    leftCamera = cv2.VideoCapture(cv2.CAP_DSHOW + 0)  # cv2.CAP_DSHOW changes internal api stuff for opencv
    rightCamera = cv2.VideoCapture(cv2.CAP_DSHOW + 1)  # add/remove cv2.CAP_DSHOW as needed for your system
    # rightCamera = cv2.VideoCapture(cv2.CAP_DSHOW + 0)
    errorTolerance = 2  # defines the amount of skipped/incomplete iterations before the loop is restarted
    iterationsToAverage = 9  # use n+1 to calculate true number averaged

    # defining opencv objects
    orb = cv2.ORB_create(nfeatures=1000)  # orb feature detector object
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)  # matcher object
    stereo = cv2.StereoSGBM_create()  # stereo object

    leftK, rightK, leftDistC, rightDistC = loadFiles()

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

    leftCamera.release()
    rightCamera.release()
    cv2.destroyAllWindows()
    Logger.shutdown()  # Shuts down the logging system and prints a closing message to the file
    sys.exit(0)
