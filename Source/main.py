# Built in python libs
import os
import sys
import time

# Additional libs
import numpy as np
import cv2

# Custom imports
try:
    from logger.logger import Logger
    from logger.loggingCalls import logArguments, logSysteminfo
    from Source.utilities import exceptions
    from cameras.cameras import writeKandDistNPZ, loadUndistortionFiles, fetchAndShowCameras, initCameras, closeCameras
    from cameras.DisplayManager import DisplayManager, createDisplaySourceData
    from visualOdometry.visualodometry import computeDisparity
    from features import computeMatchingPoints, getPointsFromKeypoints
    from objectDetection.featureDensity import findFeatureDenseBoundingBoxes
    from utilities.timing import getAvgTimeArr
    from utilities.arguments import getArgDict, getArgFlags, handleRecordFlag, handleClearLogFlag, handleVideoFlag, handleRecordFlagClose, handleThreadedDisplayFlag
except ImportError:
    from Source.logger.logger import Logger
    from Source.logger.loggingCalls import logArguments, logSysteminfo
    from Source.utilities import exceptions
    from Source.cameras.cameras import writeKandDistNPZ, loadUndistortionFiles, fetchAndShowCameras, initCameras, closeCameras
    from Source.cameras.DisplayManager import DisplayManager, createDisplaySourceData
    from Source.visualOdometry.visualodometry import computeDisparity
    from Source.features import computeMatchingPoints, getPointsFromKeypoints
    from Source.objectDetection.featureDensity import findFeatureDenseBoundingBoxes
    from Source.utilities.timing import getAvgTimeArr
    from Source.utilities.arguments import getArgDict, getArgFlags, handleRecordFlag, handleClearLogFlag, handleVideoFlag, handleRecordFlagClose, handleThreadedDisplayFlag

# Primary function where our main control flow will happen
# Contains a while true loop for continous iteration
def main():
    numTotalIterations, consecutiveErrors, iterationCounter = 0, 0, 0
    iterationTimes, cameraFTs, featureFTs, objectDectFTs, disparityFTs = list(), list(), list() , list(), list()
    leftImage, rightImage, grayLeftImage, grayRightImage = None, None, None, None
    leftPts, rightPts, leftKp, leftDesc, rightKp, rightDesc = None, None, None, None, None, None
    featureDenseBoundingBoxes = None
    disparityMap = None
    while True:
        iterationStartTime = time.perf_counter()
        try:
            # need to save previous images (if they exist) for visual odometry
            prevLeftImage, prevRightImage = leftImage, rightImage
            prevGrayLeftImage, prevGrayRightImage = grayLeftImage, grayRightImage

            # save previous feature information
            prevLeftPts, prevRightPts = leftPts, rightPts
            prevLeftKp, prevRightKp = leftKp, rightKp
            prevLeftDesc, prevRightDesc = leftDesc, rightDesc
            prevFeatureDenseBoundingBoxes = featureDenseBoundingBoxes

            # save previous frame visual odometry information
            prevDisparityMap = disparityMap

            cameraStartTime = time.perf_counter()
            # Satisfies that read images stage of control flow
            leftImage, rightImage, grayLeftImage, grayRightImage = fetchAndShowCameras(leftCam, rightCam,
                                                                                    show=not HEADLESS,
                                                                                    threadedDisplay=THREADED_DISPLAY)
            cameraFTs.append(time.perf_counter() - cameraStartTime)

            featureStartTime = time.perf_counter()
            # feature points for left and right images
            # the point at index [0], [1], [2], etc. in both is the same real life feature,
            leftPts, rightPts, leftKp, leftDesc, rightKp, rightDesc = computeMatchingPoints(grayLeftImage,
                                                                                            grayRightImage, orb,
                                                                                            matcher, show=not HEADLESS,
                                                                                    threadedDisplay=THREADED_DISPLAY)
            featureFTs.append(time.perf_counter() - featureStartTime)

            featureDenseStartTime = time.perf_counter()
            # acquires the bounding box cordinates for areas of the image where there are dense features
            featureDenseBoundingBoxes = findFeatureDenseBoundingBoxes(leftImage, getPointsFromKeypoints(leftKp),
                                                                      binSize=30.0, featuresPerPixel=0.03,
                                                                      show=not HEADLESS,
                                                                      threadedDisplay=THREADED_DISPLAY)
            objectDectFTs.append(time.perf_counter() - featureDenseStartTime)

            disparityStartTime = time.perf_counter()
            # this disparity map calculation should maybe get removed since we ??only?? care about the depth values
            disparityMap = computeDisparity(stereo, grayLeftImage, grayRightImage, show=not HEADLESS)
            disparityFTs.append(time.perf_counter() - disparityStartTime)

            # all additional functionality should be present within the === comments
            # additional data that needs to be stored for each iteration should be handled above
            #===========================================================================================================
            # TODO
            # Fill in remainder of functionality



            #===========================================================================================================
            # handles saving the video feed
            if RECORD:
                leftWriter.write(leftImage)
                rightWriter.write(rightImage)
            # Resets the consecutive error count if a full iteration is completed
            consecutiveErrors = 0
            # cv2.waitKey is needed for opencv to properly display images (think of it like a timer or interrupt)
            if not HEADLESS:
                keyPressed = cv2.waitKey(1) & 0xFF
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
            if iterationCounter != 0:
                iterationTimes.append(time.perf_counter() - iterationStartTime)
            iterationCounter += 1
        else:
            iterNum = "#{} Total Iterations: ".format(numTotalIterations + 1)
            iterTimeStr = "Avg iteration: {} {}".format(getAvgTimeArr(iterationTimes, iterationCounter), "ms")
            cameraTimeStr = " => Avg frame: {} {}".format(getAvgTimeArr(cameraFTs, iterationCounter), 'ms')
            featureTimeStr = ", Avg features: {} {}".format(getAvgTimeArr(featureFTs, iterationCounter), 'ms')
            objectDectTimeStr = ", Avg feature density: {} {}".format(getAvgTimeArr(objectDectFTs,
                                                                                    iterationCounter), 'ms')
            disparityTimeStr = ", Avg disparity map: {} {}".format(getAvgTimeArr(disparityFTs,
                                                                                 iterationCounter), 'ms')
            Logger.log(iterNum + iterTimeStr + cameraTimeStr + featureTimeStr + objectDectTimeStr + disparityTimeStr)
            iterationCounter = 0
            iterationTimes = []
            cameraFTs = []
            featureFTs = []
            objectDectFTs = []
            disparityFTs = []
        numTotalIterations += 1

# denotes program entered in this file, the main thread
if __name__ == "__main__":
    # get dictionary with args
    argDict = getArgDict()
    # sets global flags from boolean arguments
    HEADLESS, CLEAR_LOG, RECORD, THREADED_DISPLAY = getArgFlags(argDict)

    # clears log file if the CLEAR_LOG is present
    handleClearLogFlag(CLEAR_LOG)
    # begin logging and other startup methods for primary control flow
    Logger.init("log.log")  # Starts the logger and sets the logger to log to the specified file.
    # ensure logger init is done before logging anything
    time.sleep(1)
    # log system info
    logSysteminfo(Logger)
    # log all arguments
    logArguments(Logger, argDict)

    # Global constants for any hyper parameters for the code or physical constants
    # Define any global constants
    errorTolerance = 2  # defines the amount of skipped/incomplete iterations before the loop is restarted
    iterationsToAverage = 9  # use n+1 to calculate true number averaged

    # defining opencv objects
    orb = cv2.ORB_create(nfeatures=1000)  # orb feature detector object
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)  # matcher object
    # stereo object
    stereo = cv2.StereoSGBM_create(minDisparity=5, numDisparities=32, blockSize=3, P1=128, P2=512, disp12MaxDiff=0,
                                   preFilterCap=0, uniquenessRatio=5, speckleWindowSize=50, speckleRange=1)

    # inits the DisplayManager
    DisplayManager.init()

    leftCam, rightCam = handleVideoFlag(argDict['video'])

    initCameras(leftCam, rightCam, setExposure=False)

    leftWriter, rightWriter = handleRecordFlag(RECORD, leftCam, rightCam)

    handleThreadedDisplayFlag(THREADED_DISPLAY)

    # being primary loop
    Logger.log("Program starting...")
    while True:
        Logger.log("Starting loop...")
        main()
        Logger.log("Shutdown loop...")
        # sleep and then check for keyboardInterupt will fully kill program
        time.sleep(1)
        keyPressed = cv2.waitKey(1) & 0xFF
        if keyPressed == 27:
            Logger.log("Program shutdown...")
            break

    closeCameras()
    handleRecordFlagClose(leftWriter, rightWriter)
    DisplayManager.stopDisplays()
    cv2.destroyAllWindows()
    Logger.shutdown()  # Shuts down the logging system and prints a closing message to the file
    sys.exit(0)
