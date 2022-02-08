# Built in python libs
import sys
import os
from argparse import ArgumentParser, Namespace
from typing import Dict

# Additional libs
import cv2
import numpy as np

# Custom imports
try:
    from logger.logger import Logger
    from cameras.cameras import fetchCameraImages
except ImportError:
    from logger.logger import Logger
    from cameras.cameras import fetchCameraImages

def getArguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-H", "--headless", help="Do not show debug windows", action='store_true', required=False)
    parser.add_argument("-TD", "--threadeddisplay", help="Use threads to speed up displays in headed mode",
                        action="store_true", required=False)
    parser.add_argument("-R", "--record", help="Record the camera inputs to videos", action='store_true',
                        required=False)
    parser.add_argument("-CL", "--clearlog", help="Clears the log on running the program", action='store_true',
                        required=False)
    parser.add_argument("-V", "--video", help="Set a video folder which contains a left and right camera feed",
                        nargs='?', const='Data/Cameras/DefaultVideo/')
    args = parser.parse_args()
    return args

def getArgDict() -> Dict:
    # gets the arguments for the program
    args = getArguments()
    argDict = dict()
    argDict['headless'] = True if args.headless else False
    argDict['threadeddisplay'] = True if args.threadeddisplay else False
    argDict['record'] = True if args.record else False
    argDict['clearlog'] = True if args.clearlog else False
    # finds the video directory
    if args.video is not None:
        counter = 0
        while not os.path.isdir(args.video):
            args.video = "../" + args.video
            counter += 1
            if counter > 3:
                raise Exception("Video Argument: Could not find specified folder")
    argDict['video'] = args.video
    return argDict

def getArgFlags(argDict: Dict) -> (bool, bool, bool, bool):
    # HEADLESS, CLEAR_LOG, RECORD, THREADED_DISPLAY
    return argDict['headless'], argDict['clearlog'], argDict['record'], argDict['threadeddisplay']

# make video writers for record flag
def handleRecordFlag(RECORD: bool, leftCam: int, rightCam: int) -> (cv2.VideoWriter, cv2.VideoWriter):
    # initiate writers
    leftWriter = None
    rightWriter = None
    if RECORD:
        videoPath = "Data/Cameras/RawOutput/"
        while not os.path.isdir(videoPath):
            videoPath = "../" + videoPath
        leftImage, rightImage = fetchCameraImages(leftCam, rightCam)
        height, width, _ = leftImage.shape
        fourcc = cv2.VideoWriter_fourcc('W', 'M', 'V', '2')
        fps = 16.0
        leftWriter = cv2.VideoWriter(videoPath + "leftOutput.wmv", fourcc=fourcc, fps=fps, frameSize=(width, height))
        rightWriter = cv2.VideoWriter(videoPath + "rightOutput.wmv", fourcc=fourcc, fps=fps, frameSize=(width, height))
    return leftWriter, rightWriter

def handleRecordFlagClose(leftWriter: cv2.VideoWriter, rightWriter: cv2.VideoWriter):
    if leftWriter is not None:
        leftWriter.release()
    if rightWriter is not None:
        rightWriter.release()

# wipes the log ahead of the logger being restarted
def handleClearLogFlag(CLEAR_LOG: bool, logFile="log.log"):
    if CLEAR_LOG:
        with open(logFile, 'r+') as f:
            f.truncate(0)
            f.seek(0)

def handleVideoFlag(video: str) -> (str, str):
    # loading data for cameras and starting the camera process
    if video is None:
        leftCam = cv2.CAP_DSHOW + 0  # cv2.CAP_DSHOW changes internal api stuff for opencv
        rightCam = cv2.CAP_DSHOW + 1  # add/remove cv2.CAP_DSHOW as needed for your system
    else:
        leftCam = video + "stereo_left.avi"
        rightCam = video + "stereo_right.avi"
    return leftCam, rightCam

def handleThreadedDisplayFlag(THREADED_DISPLAY: bool):
    # if the displays are in threaded mode then we need a new screen to capture the keyboard
    if THREADED_DISPLAY:
        input_image = np.zeros((300, 300))
        cv2.imshow("Input Screen", input_image)