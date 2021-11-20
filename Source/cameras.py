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


# Function to get the new frames from both cameras
# "Safe" such that it will throw an exception if the cameras do not yield frames
# Takes both cameras as left and right
# Returns both image in leftImage, rightImage
# Left image in return tuple corresponds to left camera number in return tuple
@jit(forceobj=True)  # forceobj is used here since the opencv videoCaptures cannot be compiled
def readCameras(left, right):
    # Got image boolean and retrieved image
    gotLeft = left.grab()
    gotRight = right.grab()
    # Ensure images were received
    if not gotLeft:
        raise exceptions.CameraReadError("Left")
    if not gotRight:
        raise exceptions.CameraReadError("Right")
    # Return images in tuple format
    return left.retrieve()[1], right.retrieve()[1]


# TODO
# np.concatenate is a slow operation on the CPU
# using numba it is possible to put on the GPU, @cuda.jit('void(int8[:,:,:], int8[:,:,:])')

# Function makes a window which displays both camera feeds next to each other
# Takes the images as two arguments: left, right images
# Has no return value
@jit(forceobj=True)
def showCameras(left, right):
    if (left.shape != right.shape):
        minHeight = min(left.shape[0], right.shape[0])
        minWidth = min(left.shape[1], right.shape[1])
        newDim = (minWidth, minHeight)
        leftResize = cv2.resize(left, newDim)
        rightResize = cv2.resize(right, newDim)
        cv2.imshow("Combined camera output", np.concatenate((leftResize, rightResize), axis=1))
    else:
        cv2.imshow("Combined camera output", np.concatenate((left, right), axis=1))


# TODO
# Figure out how to get numba to compile an except statement
# numba can only do a basic try:, except:, need to figure out how to pass on errors with numba compilation

# Convenience function which will read and show the images given by readCameras and showCameras
# Will pass on exceptions
def readAndShowCameras(leftCam, rightCam):
    try:
        leftImage, rightImage = readCameras(leftCam, rightCam)
        undistLeft, undistRight = undistortImages(leftImage, rightImage)
        showCameras(undistLeft, undistRight)
        return undistLeft, undistRight
    except Exception as e:
        raise e

# TODO
# Look into numba or JIT compilations for undistort

# Function for undistorting the read in images
# Utilizes pre-saved camera coefficient matrices and dist coeff arrays
# Takes two images(np arrays of shape (w,h,c)) as parameters
# returns the undistorted images or raises an exception
def undistortImages(left, right):
    try:
        calibrationPath = os.path.abspath(os.path.join(os.pardir)) + "\Data\Calibration\\"
        leftK = np.load(calibrationPath + "leftK.npy")
        rightK = np.load(calibrationPath + "rightK.npy")
        leftDistC = np.load(calibrationPath + "leftDistC.npy")
        rightDistC = np.load(calibrationPath + "rightDistC.npy")
        leftNewK, _ = cv2.getOptimalNewCameraMatrix(leftK, leftDistC, (left.shape[1], left.shape[0]), 1, (left.shape[1], left.shape[0]))
        rightNewK, _ = cv2.getOptimalNewCameraMatrix(rightK, rightDistC, (right.shape[1], right.shape[0]), 1, (right.shape[1], right.shape[0]))
        return cv2.undistort(left, leftK, leftDistC, None, leftNewK), cv2.undistort(right, rightK, rightDistC, None, rightNewK)
    except FileNotFoundError:
       raise FileNotFoundError("File missing in undistortImages")
    except:
        raise exceptions.UndistortImageError()

# Function to write K matrix and dist coeffs to npz files
# K matrix is a 3x3 and dist coeffs is of length 4
def writeKandDistNPZ(lk, rk, ld, rd):
    # Gets the path to the Calibration folder in data for any computer
    calibrationPath = os.path.abspath(os.path.join(os.pardir)) + "\Data\Calibration\\"
    # saves the np.arrays inputed to their respective files
    np.save(calibrationPath + "leftK.npy", lk)
    np.save(calibrationPath + "rightK.npy", rk)
    np.save(calibrationPath + "leftDistC.npy", ld)
    np.save(calibrationPath + "rightDistC.npy", rd)
