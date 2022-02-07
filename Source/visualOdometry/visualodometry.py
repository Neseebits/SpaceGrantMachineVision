# Built in python libs
import os
import sys
import time
from multiprocessing import Process, Queue

# Additional libs
import numpy as np
import cv2
from numba import jit

# Custom  imports
try:
    import exceptions
    from cameras.DisplayManager import DisplayManager
except ImportError:
    from Source import exceptions
    from Source.cameras.DisplayManager import DisplayManager

# compute the disparity map of the two grayscale images given
# takes a stereo matcher object and two grayscale images
# @jit(forceobj=True)
def computeDisparity(stereo, left, right, show=False, threadedDisplay=True):
    # TODO
    # implement kevin's visual odometry disparity map stuff here, although I think this is pretty close?????
    disparity = stereo.compute(left, right).astype(np.float32) # <---- 30% of compute time is this line
    disparity = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    if show:
        if threadedDisplay:
            DisplayManager.show("Disparity map", disparity)
        else:
            cv2.imshow("Disparity map", disparity)
    return disparity

# multiprocessed disparity map calculation
# uses mp Queue to transfer images
def multiProcessComputeDisparity(leftQueue, rightQueue, disparityQueue):
    # stereo object
    stereo = cv2.StereoSGBM_create(minDisparity=5, numDisparities=32, blockSize=3, P1=128, P2=512, disp12MaxDiff=0,
                                   preFilterCap=0, uniquenessRatio=5, speckleWindowSize=50, speckleRange=1)
    while True:
        disparity = computeDisparity(stereo, leftQueue.get(), rightQueue.get(), show=False, threadedDisplay=False)
        # if the queue is not empty, we must clear it then push the new disparity
        # while not disparityQueue.empty():
        #     _ = disparityQueue.get()
        disparityQueue.put(disparity)

def putCameraFrames(left, right, leftQ, rightQ):
    leftQ.put(left)
    rightQ.put(right)

def getDisparityMap(dQueue):
    return dQueue.get()

def initVisualOdometry():
    leftQ, rightQ, dQueue = Queue(), Queue(), Queue()
    p = Process(target=multiProcessComputeDisparity, args=(leftQ, rightQ, dQueue,), daemon=True)
    p.start()
    return leftQ, rightQ, dQueue

# BELOW IS DONG LEES VISUAL ODOMETRY CODE
# ==================================================

# pretty sure this is legacy stuff we do not need anymore
#Returns the list of file names from the left folder.
def return_left_samples():
    listOfFilesLeft = os.listdir(os.path.join(os.path.dirname(__file__) + "./images/left"))
    listOfFilesLeft.sort()
    return listOfFilesLeft

#Returns the list of file names from the right folder.
def return_right_samples():
    listOfFilesRight = os.listdir(os.path.join(os.path.dirname(__file__) + "./images/right"))
    listOfFilesRight.sort()
    return listOfFilesRight

# this is implemented with orb in the
#https://medium.com/machine-learning-world/feature-extraction-and-similar-image-search-with-opencv-for-newbies-3c59796bf774
#Extracts features of an image via using KAZE.
def extract_features(image_path, vector_size=32):
    print("The passed image path is: " + str(image_path))
    image = cv2.imread(image_path, 0)
    alg = cv2.KAZE_create()
    kps = alg.detect(image)
    kps = sorted(kps, key=lambda x: -x.response)[:vector_size]
    kps, dsc = alg.compute(image, kps)
    needed_size = (vector_size * 64)
    return kps

#https://pythonprogramming.net/feature-matching-homography-python-opencv-tutorial/
def prep_left_and_right_samples():
    leftImgDir = "./images/left/" + str(return_left_samples()[0])
    rightImgDir = "./images/right/" + str(return_right_samples()[0])
    img1 = cv2.imread(leftImgDir, 0)
    img2 = cv2.imread(rightImgDir, 0)
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1,des2)
    matches = sorted(matches, key = lambda x:x.distance)
    
    min_dist = -1
    for match in matches:
        if min_dist == -1:
            # https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_matcher/py_matcher.html
            # Descriptor is a term to describe an encapsualted values like distances, orientation, etc ... of a match.
            min_dist = match.distance
        if match.distance < min_dist:
            min_dist = match.distance
    
    goodDistanceDiffs = []
    for m in matches:
        if m.distance < 3.0 * min_dist:
            goodDistanceDiffs.append(m)
    matches = sorted(goodDistanceDiffs, key=lambda x: x.distance)

    # img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:10],None, flags=2)
    # plt.imshow(img3)
    # plt.show()

    # (x, y) coordinates from the first image.    
    dst_pts = np.float32([kp1[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    # (x, y) coordinates from the second image.
    src_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    dst_pts = np.array(dst_pts)
    src_pts = np.array(src_pts)

    # Grabs only the first column (x values)
    dst_pts_x_translation = getTranslationX(dst_pts[:, 0][:, 0])
    # Grabs only the second column (y values)
    dst_pts_y_translation = getTranslationY(dst_pts[0, :][0, :])
    # Apply the same process to the belows
    src_pts_x_translation = getTranslationX(src_pts[:, 0][:, 0])
    src_pts_y_translation = getTranslationY(src_pts[0, :][0, :])

    return 'mock and stubs'

def getTranslationX(array_x):
    x_val_sum = 0
    for element in array_x:
        x_val_sum += element
    
    return x_val_sum / len(array_x)

def getTranslationY(array_y):
    y_val_sum = 0
    for element in array_y:
        y_val_sum += element
    
    return y_val_sum / len(array_y)