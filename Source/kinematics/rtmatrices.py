# Built in python libs
import os
import sys
import time
import math

# Additional libs
import numpy as np
from numba import jit

# Custom  imports
from Source import exceptions

@jit(nopython=True)
def getTranslationVector(deltaX=0, deltaY=0, deltaZ=0):
    return np.array([[deltaX, deltaY, deltaZ]]).T

@jit(nopython=True)
def xRotation(theta=0):
    return np.array([[1.0,0.0,0.0],[0.0,math.cos(theta),-math.sin(theta)],[0.0,math.sin(theta),math.cos(theta)]])

@jit(nopython=True)
def yRotation(theta=0):
    return np.array([[math.cos(theta),0.0,math.sin(theta)],[0.0,1.0,0.0],[-math.sin(theta),0.0,math.cos(theta)]])

@jit(nopython=True)
def zRotation(theta=0):
    return np.array([[math.cos(theta), -math.sin(theta),0.0],[math.sin(theta), math.cos(theta), 0.0],[0.0,0.0,1.0]])

# @jit(nopython=True)
@jit(forceobj=True)
def getRotationMatrix(thetaX=0, thetaY=0, thetaZ=0):
    return zRotation(thetaZ) @ yRotation(thetaY) @ xRotation(thetaX)

# @jit(nopython=True)
@jit(forceobj=True)
def getTransformationMatrix(thetaX=0, thetaY=0, thetaZ=0, deltaX=0, deltaY=0, deltaZ=0):
    return np.block([[getRotationMatrix(thetaX, thetaY, thetaZ), getTranslationVector(deltaX, deltaY, deltaZ)], [0, 0, 0, 1]])

def compile_rtmatrices(verbose=False):
    if verbose:
        print("Compiling rtmatrices...")
        startTime = time.time()
    getTransformationMatrix(thetaX=1, thetaY=1, thetaZ=1, deltaX=1, deltaY=1, deltaZ=1)
    if verbose:
        print("   Compiling took: {} seconds".format(time.time() - startTime))

# this is here so upon import the code will compile
compile_rtmatrices()