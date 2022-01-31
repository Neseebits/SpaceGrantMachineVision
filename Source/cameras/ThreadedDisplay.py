from threading import Thread
import cv2

class ThreadedDisplay:
    """
    Class that continuously shows a frame using a dedicated thread.
    """

    def __init__(self, windowName="Output", frame=None):
        self.frame = frame
        self.windowName = windowName
        self.stopped = False

    def start(self):
        thread = Thread(target=self.show, args=())
        thread.setDaemon(True)
        thread.start()
        return self

    def show(self):
        while not self.stopped:
            cv2.imshow(self.windowName, self.frame)
            keyPressed = cv2.waitKey(10) & 0xFF
            if keyPressed == 27:
                self.stopped = True

    def update(self, newFrame):
        self.frame = newFrame

    def stop(self):
        self.stopped = True