import constants as c
from gui.windows import VideoStream

from PIL import Image, ImageTk
import io


class AbstractRobot(object):
    def __init__(self, connection):
        self.connection = connection
        """ @type : Connections.ConnectionProcessEnd.RobotConnection """
        self.socket = None
        self.stream = None
        self.bytes = None
        self.window = None
        self.psychopy_disabled = None
        self.stream_enabled = None
        self.connection.waitMessages(self.start, self.exit, self.update, self.setup, self.sendMessage, poll=0)

    def handleMessage(self, message):
        raise NotImplementedError("handleMessage not implemented!")

    def getVideoStreamBytes(self):
        raise NotImplementedError("getVideoStreamBytes not implemented!")

    def start(self):
        while True:
            self.update()
            message = self.connection.receiveMessageInstant()
            if message is not None:
                if self.handleMessage(message):
                    pass
                elif isinstance(message, basestring):
                    return message
                else:
                    print("Robot message: " + str(message))

    def updateVideo(self):
        if self.stream_enabled:
            new_bytes = self.getVideoStreamBytes()
            if new_bytes is not None:
                self.bytes += new_bytes
                start = self.bytes.find('\xff\xd8')
                end = self.bytes.find('\xff\xd9')
                if start != -1 and end != -1:
                    bytes_start_to_end = self.bytes[start:end+2]
                    self.bytes = self.bytes[end+2:]
                    image = ImageTk.PhotoImage(Image.open(io.BytesIO(bytes_start_to_end)))
                    self.sendImageToStreamingWindow(image)

    def sendImageToStreamingWindow(self, image):
        if self.psychopy_disabled is not None:
            if self.psychopy_disabled:
                self.window.updateStream(image)
            else:
                self.connection.sendMessage(image)

    def updateWindow(self):
        if self.window is not None:
            self.window.update()

    def exitWindow(self):
        if self.window is not None:
            self.window.exitFlag = True
            self.window.exit()

    def update(self):
        self.updateVideo()
        self.updateWindow()

    def exit(self):
        self.exitWindow()
        self.connection.close()

    def sendRobotMessage(self, message):
        raise NotImplementedError("sendRobotMessage not implemented!")

    def sendMessage(self, message):
        if message in c.ROBOT_COMMANDS:
            self.sendRobotMessage(message)
        else:
            print("Unknown message in Robot: " + str(message))

    def psychopyDisabled(self, options):
        return options[c.DISABLE] == 1 if c.DISABLE in options else None

    def streamEnabled(self, options):
        return options[c.ROBOT_STREAM] == 1

    def setupVideoStream(self):
        raise NotImplementedError("setupVideoStream not implemented!")

    def setupStreamingWindow(self, psychopy_disabled):
        if psychopy_disabled:
            window = VideoStream.StreamWindow()
            window.setup()
            return window
        else:
            return None

    def setupStreaming(self, stream_enabled, psychopy_disabled):
        if stream_enabled:
            return self.setupStreamingWindow(psychopy_disabled)
        else:
            return None

    def subclassSetup(self, options):
        raise NotImplementedError("subclassSetup not implemented!")

    def setup(self):
        options = self.connection.receiveMessageBlock()
        self.exitWindow()
        self.stream_enabled = self.streamEnabled(options[c.DATA_ROBOT])
        self.psychopy_disabled = self.psychopyDisabled(options[c.DATA_BACKGROUND])
        self.subclassSetup(options)
        self.window = self.setupStreaming(self.stream_enabled, self.psychopy_disabled)
        return self.setupVideoStream()
