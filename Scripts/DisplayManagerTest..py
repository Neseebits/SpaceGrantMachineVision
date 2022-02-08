from cameras.DisplayManager import DisplayManager, createDisplaySourceData
import cv2

if __name__ == '__main__' :
    cam1 = cv2.VideoCapture(0)
    cam2 = cv2.VideoCapture(1)

    got1, frame1 = cam1.read()
    got2, frame2 = cam2.read()

    display1 = createDisplaySourceData("Camera 1", frame1)
    display2 = createDisplaySourceData("Camera 2", frame2)
    DisplayManager.showGroup([display1, display2])

    while True:
        got1, frame1 = cam1.read()
        got2, frame2 = cam2.read()

        DisplayManager.show("Camera 1", frame1)
        DisplayManager.show("Camera 2", frame2)

        keyPressed = cv2.waitKey(10) & 0xFF
        if keyPressed == 27:
            break