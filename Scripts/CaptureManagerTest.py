from Source.cameras.CaptureManager import CaptureManager, createSourceData
import cv2

if __name__ == '__main__' :
    source1 = createSourceData(0)
    source2 = createSourceData(1)
    CaptureManager.init([source1, source2])

    while True:
        cv2.imshow("Source 1", CaptureManager.getFrame(0))
        cv2.imshow("Source 2", CaptureManager.getFrame(1))

        keyPressed = cv2.waitKey(10) & 0xFF
        if keyPressed == 27:
            break