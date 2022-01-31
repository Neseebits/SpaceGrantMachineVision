from threading import Thread
import cv2

class ThreadedCapture:
    """
        Class that continuously gets frames from a VideoCapture object
        with a dedicated thread.
    """
    def __init__(self, source, K=None, distC=None, setExposure=False, autoExposure=1.0, exposure=100.0):
        # basic checking with asserts that all data is present
        if (K is not None) or (distC is not None):
            assert ((K is not None) and (distC is not None)), "If K or distC is defined, then both must be defined"
        # define flow controllers
        self.stopped = False
        self.success = True
        # define source, camera intrinsic matrix, distortion coefficients, and exposure settings
        self.source = source
        self.frame = None
        self.K = K
        # results from cv2.getOptimalNewCameraMatrix
        self.newK, self.roi, self.x, self.y, self.w, self.h = None, None, None, None, None, None
        self.distC = distC
        self.setExposure = setExposure
        self.autoExposure = autoExposure
        self.exposure = exposure
        # create the cv2 video capture to acquire either the recorded video or webcam
        try:
            self.capture = cv2.VideoCapture(source)
        except:
            raise Exception("Error defining cv2.videoCapture object for source: {}".format(self.source))
        # set exposures if option set
        try:
            if self.setExposure:
                self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, autoExposure)
                self.capture.set(cv2.CAP_PROP_EXPOSURE, exposure)
        except:
            raise Exception("Error settings exposure for video source: {}".format(self.source))
        # create undistortion K matrix
        try:
            success, frame = self.capture.read()
            if (self.K is not None) and (self.distC is not None):
                h, w = frame.shape[:2]
                self.newK, self.roi = cv2.getOptimalNewCameraMatrix(self.K, self.distC, (w,h), 1, (w,h))
                self.x, self.y, self.w, self.h = self.roi
        except:
            raise Exception("Error computing new K matrix for video source: {}".format(self.source))

    # reads the most recent image from the camera and saves it to self.frame
    def readCapture(self):
        self.success, frame = self.capture.read()
        if self.newK is not None:
            frame = cv2.undistort(frame, self.K, self.distC, None, self.newK)
            self.frame = frame[self.y:self.y+self.h, self.x:self.x+self.w]
        else:
            self.frame = frame

    def readFrames(self):
        while not self.stopped:
            if not self.success:
                self.stop()
            else:
                self.readCapture()
        self.capture.release()

    # returns the current frame
    def getFrame(self):
        return self.frame

    # starts the capture thread
    def start(self):
        thread = Thread(target=self.readFrames, args=(),)
        thread.setDaemon(True)
        thread.start()
        return self

    # stops the capture
    def stop(self):
        self.stopped = True


