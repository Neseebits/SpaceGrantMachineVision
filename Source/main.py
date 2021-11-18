# Built in python libs
import os
import sys
import time

# Additional libs
import numpy as np
import cv2

# Custom imports
import exceptions
import cameras
from cameras import readAndShowCameras

# Primary function where our main control flow will happen
# Contains a while true loop for continous iteration
def main():
    consecutiveErrors = 0
    while True:
        try:
            images = readAndShowCameras((leftCamera, rightCamera)) # Satifies that read images stage of control flow
            # Additional functions calls go here

            # TODO
            # Fill in remainder of functionality


            # Resets the consecutive error count if a full iteration is completed
            consecutiveErrors = 0
        except exceptions.KeyboardInterrupt as e: # Kills the loop if a keyboardInterrupt occurs
            print("User killed loop with: " + e.getKey())
            break
        except Exception as e:
            # Possibly instead of restarting, we might want to look into 
            print(e + " -> Occured in primary operation loop of program. Failed iterations in a row: {}").format(consecutiveErrors)
            consecutiveErrors += 1 
            if(consecutiveErrors > errorTolerance):
                print("RESTARTING PRIMARY CONTROL LOOP")
                break
            

if __name__ == "__main__":
    # Global constants for any hyperparameters for the code or physical constants
    global leftCamera
    global rightCamera
    global errorTolerance # defines the amount of skipped/incomplete iterations before the loop is restarted

    # Define any global constants
    leftCamera = cv2.VideoCapture(0)
    rightCamera = cv2.VideoCapture(1)
    errorTolerance = 1

    while True:
        print("Starting loop...")
        main()
        # sleep and then check for keyboardInterupt will fully kill program
        time.sleep(2)
        key_pressed = cv2.waitKey(10) & 0xFF
        if key_pressed == 27:
            print("Program shutdown...")
            break
    sys.exit(0)