# Built in python libs
import os
import sys
import time

# Additional libs
import numpy as np
import cv2
from numba import jit

# Custom  imports
try:
    from logger import Logger
    import exceptions
    from cameras.CaptureManager import CaptureManager, createCaptureSourceData
    from cameras.DisplayManager import DisplayManager, createDisplaySourceData
except ImportError:
    from Source.logger import Logger
    from Source import exceptions
    from Source.cameras.CaptureManager import CaptureManager, createCaptureSourceData
    from Source.cameras.DisplayManager import DisplayManager, createDisplaySourceData

# gets the camera frames from the captureManager
def fetchCameraImages(leftSource, rightSource):
    return CaptureManager.getFrame(leftSource), CaptureManager.getFrame(rightSource)

# makes grayscale images of the bgr_images returned by readCameras
# @jit(forceobj=True)
def getGrayscaleImages(left, right):
    return cv2.cvtColor(left, cv2.COLOR_BGR2GRAY), cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)

# Function makes a window which displays both camera feeds next to each other
# Takes the images as two arguments: left, right images
# Has no return value
@jit(forceobj=True)
def showCameras(left, right, threadedDisplay=True):
    if (left.shape != right.shape):
        minHeight = min(left.shape[0], right.shape[0])
        minWidth = min(left.shape[1], right.shape[1])
        newDim = (minWidth, minHeight)
        leftResize = cv2.resize(left, newDim)
        rightResize = cv2.resize(right, newDim)
        displayImg = np.concatenate((leftResize, rightResize), axis=1)
    else:
        displayImg = np.concatenate((left, right), axis=1)

    if threadedDisplay:
        DisplayManager.show("Combined camera output", displayImg)
    else:
        cv2.imshow("Combined camera output", displayImg)

# gets the camera images from the capture manager
# converts the images to grayscale
# shows the images
def fetchAndShowCameras(leftSource, rightSource, show=True, threadedDisplay=True):
    try:
        left, right = fetchCameraImages(leftSource, rightSource)
        grayLeft, grayRight = getGrayscaleImages(left, right)
        if show:
            showCameras(left, right, threadedDisplay)
        return left, right, grayLeft, grayRight
    except Exception as e:
        raise e

# creates the cameras sources for ThreadedCapture and runs them into CaptureManager
def initCameras(leftCam, rightCam, leftK, rightK, leftDistC, rightDistC, setExposure=False):
    # start CaptureManager for left and right cameras
    left = createCaptureSourceData(leftCam, leftK, leftDistC, setExposure=setExposure)
    right = createCaptureSourceData(rightCam, rightK, rightDistC, setExposure=setExposure)
    CaptureManager.init([left, right])

# closes the camera sources
def closeCameras():
    CaptureManager.stopSources()

# loads all files from data that the robot needs
def loadUndistortionFiles():
    # one time file loading for the camera intrinsic matrices and undistortion coeff
    calibrationPath = "Data/Calibration/"
    if not os.path.isdir(calibrationPath):
        calibrationPath = "../" + calibrationPath
    leftK = np.load(calibrationPath + "leftK.npy")
    rightK = np.load(calibrationPath + "rightK.npy")
    leftDistC = np.load(calibrationPath + "leftDistC.npy")
    rightDistC = np.load(calibrationPath + "rightDistC.npy")

    return leftK, rightK, leftDistC, rightDistC

# Function to write K matrix and dist coeffs to npz files
# K matrix is a 3x3 and dist coeffs is of length 4
def writeKandDistNPZ(lk, rk, ld, rd):
    # Gets the path to the Calibration folder in data for any computer
    calibrationPath = "Data/Calibration/"
    if not os.path.isdir(calibrationPath):
        calibrationPath = "../" + calibrationPath + "/"
    # saves the np.arrays inputed to their respective files
    np.save(calibrationPath + "leftK.npy", lk)
    np.save(calibrationPath + "rightK.npy", rk)
    np.save(calibrationPath + "leftDistC.npy", ld)
    np.save(calibrationPath + "rightDistC.npy", rd)

# # Function to get the new frames from both cameras
# # "Safe" such that it will throw an exception if the cameras do not yield frames
# # Takes both cameras as left and right
# # Returns both image in leftImage, rightImage
# # Left image in return tuple corresponds to left camera number in return tuple
# # @jit(forceobj=True)  # forceobj is used here since the opencv videoCaptures cannot be compiled
# def readCameras(left, right):
#     # Got image boolean and retrieved image
#     gotLeft, gotRight = left.grab(), right.grab()
#     # Ensure images were received
#     if not gotLeft:
#         raise exceptions.CameraReadError("Left")
#     if not gotRight:
#         raise exceptions.CameraReadError("Right")
#     # Return images
#     return left.retrieve()[1], right.retrieve()[1]
#
# # Convenience function which will read and show the images given by readCameras and showCameras
# # Will pass on exceptions
# def readAndShowCameras(leftCam, rightCam, leftK, rightK, leftDistC, rightDistC, show=True):
#     try:
#         leftImage, rightImage = readCameras(leftCam, rightCam)
#         undistLeft, undistRight = undistortImages(leftImage, rightImage, leftK, rightK, leftDistC, rightDistC)
#         if show:
#             showCameras(undistLeft, undistRight)
#         return undistLeft, undistRight
#     except Exception as e:
#         raise e
#
# def writeCameraImages(cameraPath, leftImage, rightImage, cameraLocks):
#     cameraLocks[0].acquire()
#     cv2.imwrite(cameraPath + "left_image.jpg", leftImage)
#     cameraLocks[0].release()
#     cameraLocks[1].acquire()
#     cv2.imwrite(cameraPath + "right_image.jpg", rightImage)
#     cameraLocks[1].release()
#
# # Function for undistorting the read in images
# # Utilizes pre-saved camera coefficient matrices and dist coeff arrays
# # Takes two images(np arrays of shape (w,h,c)) as parameters
# # returns the undistorted images or raises an exception
# def undistortImages(left, right, leftK, rightK, leftDistC, rightDistC):
#     try:
#         leftNewK, _ = cv2.getOptimalNewCameraMatrix(leftK, leftDistC, (left.shape[1], left.shape[0]), 1, (left.shape[1], left.shape[0]))
#         rightNewK, _ = cv2.getOptimalNewCameraMatrix(rightK, rightDistC, (right.shape[1], right.shape[0]), 1, (right.shape[1], right.shape[0]))
#         return cv2.undistort(left, leftK, leftDistC, None, leftNewK), cv2.undistort(right, rightK, rightDistC, None, rightNewK)
#     except FileNotFoundError:
#         raise FileNotFoundError("Cannot load calibration data in undistortImages -> cameras.py")
#     except:
#         raise exceptions.UndistortImageError("undistortImages function error")
#
# def readAndWriteCameras(cameraPath, leftCam, rightCam, leftK, rightK, leftDistC, rightDistC, cameraLocks):
#     leftImg, rightImg = readCameras(leftCam, rightCam)
#     undistortedLeft, undistortedRight = undistortImages(leftImg, rightImg, leftK, rightK, leftDistC, rightDistC)
#     writeCameraImages(cameraPath, undistortedLeft, undistortedRight, cameraLocks)
#
# def cameraProcess(cameraPath, leftCam, rightCam, leftK, rightK, leftDistC, rightDistC, cameraLocks):
#     leftCamera = cv2.VideoCapture(leftCam)
#     rightCamera = cv2.VideoCapture(rightCam)
#     while True:
#         try:
#             readAndWriteCameras(cameraPath, leftCamera, rightCamera, leftK, rightK, leftDistC, rightDistC, cameraLocks)
#         except exceptions.CameraReadError as e:
#             Logger.log(e)
#         except:
#             Logger.log("Uncaught exception in readAndWriteCameras")
#         finally:
#             time.sleep(0.064)
