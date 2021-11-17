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
        images = readAndShowCameras((leftCamera, rightCamera))

    
        # Implements a 10ms wait at the end of every loop 
        # This will allow some movement between input frames
        key_pressed = cv2.waitKey(10) & 0xFF
        if key_pressed == 27:
            break  # Quit on ESC

if __name__ == "__main__":
    # Global constants for any hyperparameters for the code or physical constants
    global leftCamera
    global rightCamera

    # Define any global constants
    leftCamera = cv2.videoReader(0)
    rightCamera = cv2.videoReader(1)

    main()