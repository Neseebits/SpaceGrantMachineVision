# Built in python libs
import os
import sys
import time

# Additional libs
import numpy as np
import cv2

# Custom imports
from logger import Logger
import exceptions
import cameras
from cameras import readAndShowCameras

# Primary function where our main control flow will happen
# Contains a while true loop for continous iteration
def main():
    consecutiveErrors = 0
    iterationCounter = 0
    iterationTimes = []
    while True:
        iterationStartTime = time.time()
        try:
            images = readAndShowCameras((leftCamera, rightCamera)) # Satifies that read images stage of control flow
            # ADDITIONAL FUNCTIONS BELOW

            # TODO
            # Fill in remainder of functionality


            # ADDITIONAL FUNCTIONS ABOVE
            # Resets the consecutive error count if a full iteration is completed
            consecutiveErrors = 0
            # cv2.waitKey is needed for opencv to properly display images (think of it like a timer or interrupt)
            keyPressed = cv2.waitKey(10) & 0xFF
            if keyPressed == 27:
                raise exceptions.KeyboardInterrupt("ESC")  # Quit on ESC
        except exceptions.KeyboardInterrupt as e: # Kills the loop if a keyboardInterrupt occurs
            Logger.log("User killed loop with: " + e.getKey())
            break
        except Exception as e:
            # Possibly instead of restarting, we might want to look into
            Logger.log(str(e) + " -> Occured in primary operation loop of program. Failed iterations in a row: {}".format(consecutiveErrors))
            consecutiveErrors += 1 
            if(consecutiveErrors > errorTolerance):
                Logger.log("RESTARTING PRIMARY CONTROL LOOP")
                break
        if iterationCounter < iterationsToAverage:
            iterationTimes.append(time.time() - iterationStartTime)
            iterationCounter += 1
        else:
            Logger.log("Average iteration time: {} {}".format(round((sum(iterationTimes)/iterationCounter)*1000, 1), "ms"))
            iterationCounter = 0
            iterationTimes = []
            

if __name__ == "__main__":
    Logger.init("log.txt") # Starts the logger and sets the logger to log to the specified file.
    # Global constants for any hyperparameters for the code or physical constants
    # Define any global constants
    leftCamera = cv2.VideoCapture(cv2.CAP_DSHOW + 0) #      cv2.CAP_DSHOW changes internal api stuff for opencv
    # rightCamera = cv2.VideoCapture(cv2.CAP_DSHOW + 1) #   add/remove cv2.CAP_DSHOW as needed for your system
    rightCamera = cv2.VideoCapture(cv2.CAP_DSHOW + 0)
    errorTolerance = 2 # defines the amount of skipped/incomplete iterations before the loop is restarted
    iterationsToAverage = 9 # use n+1 to calculate true number averaged

    Logger.log("Program starting...")
    while True:
        Logger.log("Starting loop...")
        main()
        Logger.log("Shutdown loop...")
        # sleep and then check for keyboardInterupt will fully kill program
        time.sleep(2)
        keyPressed = cv2.waitKey(10) & 0xFF
        if keyPressed == 27:
            Logger.log("Program shutdown...")
            break

    leftCamera.release()
    rightCamera.release()
    cv2.destroyAllWindows()
    Logger.shutdown()  # Shuts down the logging system and prints a closing message to the file
    sys.exit(0)