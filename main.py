# Built in python libs
import os
import sys
import time

# Additional libs
import numpy as np
import cv2

# Custom imports
import cameras
from cameras import readAndShowCameras

# Primary function where our main control flow will happen
# Contains a while true loop for continous iteration
def main():
    while True:
        try:
            images = readAndShowCameras((leftCamera, rightCamera))

        except Exception as e:
            # Possibly instead of restarting, we might want to look into 
            print(e + " -> Occured in primary operation loop of program. RESTARTING")

if __name__ == "__main__":
    # Global constants for any hyperparameters for the code or physical constants
    global leftCamera
    global rightCamera

    # Define any global constants
    leftCamera = cv2.VideoCapture(0)
    rightCamera = cv2.VideoCapture(1)

    while True:
        main()