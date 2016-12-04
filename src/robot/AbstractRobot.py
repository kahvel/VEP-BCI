

class AbstractRobot(object):
    def __init__(self):
        self.socket = None
        self.stream = None

    def handleMessage(self, message):
        raise NotImplementedError("handleMessage not implemented!")

    def getVideoStreamBytes(self):
        raise NotImplementedError("getVideoStreamBytes not implemented!")

    def setupVideoStream(self):
        raise NotImplementedError("setupVideoStream not implemented!")
