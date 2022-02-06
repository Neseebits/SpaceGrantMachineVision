# Built in python libs
import os
import sys
import time

# Additional libs
import numpy as np
import cv2
import platform
import argparse

# Custom imports
try:
    from logger import Logger
    import exceptions
    from cameras.cameras import writeKandDistNPZ, loadUndistortionFiles, fetchAndShowCameras, initCameras, closeCameras, fetchCameraImages
    from cameras.DisplayManager import DisplayManager, createDisplaySourceData
    from visualOdometry.visualodometry import computeDisparity
    from features import computeMatchingPoints, getPointsFromKeypoints
    from objectDetection.featureDensity import findFeatureDenseBoundingBoxes
    from utility import getAvgTimeArr
except ImportError:
    from Source.logger import Logger
    from Source import exceptions
    from Source.cameras.cameras import writeKandDistNPZ, loadUndistortionFiles, fetchAndShowCameras, initCameras, closeCameras
    from Source.cameras.DisplayManager import DisplayManager, createDisplaySourceData
    from Source.visualOdometry.visualodometry import computeDisparity
    from Source.features import computeMatchingPoints, getPointsFromKeypoints
    from Source.objectDetection.featureDensity import findFeatureDenseBoundingBoxes
    from Source.utility import getAvgTimeArr

# Primary function where our main control flow will happen
# Contains a while true loop for continous iteration
def main():
    numTotalIterations = 0
    consecutiveErrors = 0
    iterationCounter = 0
    iterationTimes = []
    cameraFrameTimes = []
    featureFrameTimes = []
    featureDenseFrameTimes = []
    disparityFrameTimes = []
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
            cameraFrameTimes.append(time.perf_counter() - cameraStartTime)

            featureStartTime = time.perf_counter()
            # feature points for left and right images
            # the point at index [0], [1], [2], etc. in both is the same real life feature,
            leftPts, rightPts, leftKp, leftDesc, rightKp, rightDesc = computeMatchingPoints(grayLeftImage,
                                                                                            grayRightImage, orb,
                                                                                            matcher, show=not HEADLESS,
                                                                                    threadedDisplay=THREADED_DISPLAY)
            featureFrameTimes.append(time.perf_counter() - featureStartTime)

            featureDenseStartTime = time.perf_counter()
            # acquires the bounding box cordinates for areas of the image where there are dense features
            featureDenseBoundingBoxes = findFeatureDenseBoundingBoxes(leftImage, getPointsFromKeypoints(leftKp),
                                                                      binSize=30.0, featuresPerPixel=0.03,
                                                                      show=not HEADLESS,
                                                                      threadedDisplay=THREADED_DISPLAY)
            featureDenseFrameTimes.append(time.perf_counter() - featureDenseStartTime)

            disparityStartTime = time.perf_counter()
            # this disparity map calculation should maybe get removed since we ??only?? care about the depth values
            disparityMap = computeDisparity(stereo, grayLeftImage, grayRightImage, show=not HEADLESS)
            disparityFrameTimes.append(time.perf_counter() - disparityStartTime)

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
            cameraTimeStr = " => Avg frame: {} {}".format(getAvgTimeArr(cameraFrameTimes, iterationCounter), 'ms')
            featureTimeStr = ", Avg features: {} {}".format(getAvgTimeArr(featureFrameTimes, iterationCounter), 'ms')
            objectDectTimeStr = ", Avg feature density: {} {}".format(getAvgTimeArr(featureDenseFrameTimes,
                                                                                    iterationCounter), 'ms')
            disparityTimeStr = ", Avg disparity map: {} {}".format(getAvgTimeArr(disparityFrameTimes,
                                                                                 iterationCounter), 'ms')
            Logger.log(iterNum + iterTimeStr + cameraTimeStr + featureTimeStr + objectDectTimeStr + disparityTimeStr)
            iterationCounter = 0
            iterationTimes = []
            cameraFrameTimes = []
            featureFrameTimes = []
            featureDenseFrameTimes = []
            disparityFrameTimes = []
        numTotalIterations += 1

# denotes program entered in this file, the main thread
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--headless", help="Do not show debug windows", action='store_true', required=False)
    parser.add_argument("-TD", "--threadeddisplay", help="Use threads to speed up displays in headed mode",
                        action="store_true", required=False)
    parser.add_argument("-R", "--record", help="Record the camera inputs to videos", action='store_true',
                        required=False)
    parser.add_argument("-CL", "--clearlog", help="Clears the log on running the program", action='store_true',
                        required=False)
    args = parser.parse_args()
    HEADLESS = True if args.headless else False
    THREADED_DISPLAY = True if args.threadeddisplay else False
    RECORD = True if args.record else False
    CLEAR_LOG = True if args.clearlog else False

    # wipes the log ahead of the logger being restarted
    if CLEAR_LOG:
        with open("log.log", 'r+') as f:
            f.truncate(0)
            f.seek(0)

    # begin logging and other startup methods for primary control flow
    Logger.init("log.log")  # Starts the logger and sets the logger to log to the specified file.

    # Log system information
    Logger.log("SYSTEM INFORMATION:")
    Logger.log(f"   Python Version: {sys.version}")
    uname = platform.uname()
    Logger.log(f"   System: {uname.system}")
    Logger.log(f"   Node Name: {uname.node}")
    Logger.log(f"   Release: {uname.release}")
    Logger.log(f"   Version: {uname.version}")
    Logger.log(f"   Machine: {uname.machine}")
    Logger.log(f"   Processor: {uname.processor}")

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

    # loading data for cameras and starting the camera process
    leftCam = cv2.CAP_DSHOW + 0  # cv2.CAP_DSHOW changes internal api stuff for opencv
    rightCam = cv2.CAP_DSHOW + 1  # add/remove cv2.CAP_DSHOW as needed for your system
    leftK, rightK, leftDistC, rightDistC = loadUndistortionFiles()
    initCameras(leftCam, rightCam, leftK, rightK, leftDistC, rightDistC, setExposure=False)
    # sleep time for cameras to read in a frame
    leftImage, rightImage = fetchCameraImages(leftCam, rightCam)
    while leftImage is None or rightImage is None:
        time.sleep(.01)
        leftImage, rightImage = fetchCameraImages(leftCam, rightCam)
    # initiate writers
    leftWriter = None
    rightWriter = None
    if RECORD:
        videoPath = "Data/Cameras/"
        while not os.path.isdir(videoPath):
            videoPath = "../" + videoPath
        leftImage, rightImage = fetchCameraImages(leftCam, rightCam)
        height, width, _ = leftImage.shape
        fourcc = cv2.VideoWriter_fourcc('W', 'M', 'V', '2')
        fps = 24.0
        leftWriter = cv2.VideoWriter(videoPath + "leftOutput.wmv", fourcc=fourcc, fps=fps, frameSize=(width, height))
        rightWriter = cv2.VideoWriter(videoPath + "rightOutput.wmv", fourcc=fourcc, fps=fps, frameSize=(width, height))

    # if the displays are in threaded mode then we need a new screen to capture the keyboard
    if THREADED_DISPLAY:
        input_image = np.zeros((300, 300))
        cv2.imshow("Input Screen", input_image)

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
    if leftWriter is not None:
        leftWriter.release()
    if rightWriter is not None:
        rightWriter.release()
    DisplayManager.stopDisplays()
    cv2.destroyAllWindows()
    Logger.shutdown()  # Shuts down the logging system and prints a closing message to the file
    sys.exit(0)
