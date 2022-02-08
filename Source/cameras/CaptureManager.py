try:
    from cameras.ThreadedCapture import ThreadedCapture
except ImportError:
    from cameras.ThreadedCapture import ThreadedCapture

def createCaptureSourceData(source, K=None, distC=None, setExposure=False, autoExposure=1.0, exposure=100.0):
    return [source, K, distC, setExposure, autoExposure, exposure]

class CaptureManager:
    """
        Class that managers threadedCapture objects and allows access to
        frames acquired by those objects.
    """
    # generate a dict indexed by source to aggregate the threads
    sources = dict()
    # sources is a list of lists formed where each entry should be created by createSourceData
    @classmethod
    def init(cls, sources):
        # initialize and start all threads
        for src in sources:
            cls.sources[src[0]] = ThreadedCapture(src[0], src[1], src[2], src[3], src[4], src[5]).start()

    # gets the frame from a specific source
    @classmethod
    def getFrame(cls, source):
        return cls.sources[source].getFrame()

    # gets all frames from all sources
    @classmethod
    def getFrames(cls):
        frames = dict()
        for source, thread in cls.sources.items():
            frames[source] = thread.getFrame()
        return frames

    # stops a threadedCapture for source
    @classmethod
    def stopSource(cls, source):
        cls.sources[source].stop()

    # stops all sources
    @classmethod
    def stopSources(cls):
        for source, thread in cls.sources.items():
            thread.stop()
