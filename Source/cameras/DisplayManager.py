try:
    from cameras.ThreadedDisplay import ThreadedDisplay
except ImportError:
    from Source.cameras.ThreadedDisplay import ThreadedDisplay

def createDisplaySourceData(windowName="Output", frame=None):
    return [windowName, frame]

class DisplayManager:
    """
        Class that managers threadedDisplay objects
    """
    # generate a dict indexed by source to aggregate the threads
    displays = dict()
    # inits the DisplayMananger
    @classmethod
    def init(cls):
        cls.displays = dict()

    # sources is a list of lists formed where each entry should be created by createSourceData
    @classmethod
    def showGroup(cls, displays):
        # initialize and start all threads
        for display in displays:
            cls.displays[display[0]] = ThreadedDisplay(display[0], display[1]).start()

    # gets the frame from a specific source
    @classmethod
    def show(cls, windowName, frame):
        if windowName in cls.displays:
            cls.displays[windowName].update(frame)
        else:
            cls.displays[windowName] = ThreadedDisplay(windowName, frame).start()

    # stops a threadedDisplay from window name
    @classmethod
    def stopDisplay(cls, windowName):
        cls.displays[windowName].stop()

    # stops all displays
    @classmethod
    def stopDisplays(cls):
        for source, thread in cls.displays.items():
            thread.stop()