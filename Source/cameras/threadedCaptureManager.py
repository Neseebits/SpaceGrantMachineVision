from threadedCapture import threadedCapture

def createSourceData(source, K=None, distC=None, setExposure=False, autoExposure=1.0, exposure=100.0):
    return [source, K, distC, setExposure, autoExposure, exposure]

class threadedCaptureManager:
    """
        Class that managers threadedCapture objects and allows access to
        frames acquired by those objects.
    """
    # sources is a list of lists formed where each entry should be created by createSourceData
    def __init__(self, sources):
        # generate a dict indexed by source to aggregate the threads
        self.sources = dict()
        self.frames = dict()
        for source in sources:
            # initialize and start all threads
            self.sources[source[0]] = threadedCapture(source[0], source[1], source[2], source[3], source[4], source[5])
            self.sources[source[0]].start()
            self.frames[source[0]] = self.sources[source[0]].getFrame()
        
