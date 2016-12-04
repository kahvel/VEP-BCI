import constants as c
from gui_elements.windows import VideoStream
from robot import JumpingSumo, Pitank


class MessageHandler(object):
    def __init__(self, connection):
        self.connection = connection
        self.bytes = ""
        self.robot = None
        self.window = None
        self.stream_enabled = None
        self.psychopy_disabled = None
        self.target_to_command_dictionary = None
        self.connection.waitMessages(self.start, self.exit, self.update, self.setup, self.handleMessage, poll=0.1)

    def handleMessage(self, message):
        if self.robot is not None:
            self.robot.handleMessage(message)

    def update(self):
        self.updateVideo()
        self.updateWindow()

    def exit(self):
        self.exitWindow()
        self.connection.close()

    def exitWindow(self):
        if self.window is not None:
            self.window.exitFlag = True
            self.window.exit()

    def updateWindow(self):
        if self.window is not None:
            self.window.update()

    def setup(self):
        options = self.connection.receiveMessageBlock()
        self.exitWindow()
        self.robot = Pitank.Pitank()
        self.stream_enabled = self.streamEnabled(options[c.DATA_ROBOT])
        self.psychopy_disabled = self.psychopyDisabled(options[c.DATA_BACKGROUND])
        self.target_to_command_dictionary = self.targetNumberToCommandDictionary(options[c.DATA_ROBOT])
        self.window = self.setupStreaming(self.stream_enabled, self.psychopy_disabled)
        return self.robot.setupVideoStream()

    def psychopyDisabled(self, options):
        return options[c.DISABLE] == 1 if c.DISABLE in options else None

    def streamEnabled(self, options):
        return options[c.ROBOT_STREAM] == 1

    def targetNumberToCommandDictionary(self, options):
        return {
            options[c.ROBOT_OPTION_FORWARD]: c.MOVE_FORWARD,
            options[c.ROBOT_OPTION_BACKWARD]: c.MOVE_BACKWARD,
            options[c.ROBOT_OPTION_LEFT]: c.MOVE_LEFT,
            options[c.ROBOT_OPTION_RIGHT]: c.MOVE_RIGHT,
            options[c.ROBOT_OPTION_STOP]: c.MOVE_STOP
        }

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

    def start(self):
        self.bytes = ""
        while True:
            self.update()
            message = self.connection.receiveMessageInstant()
            if message is not None:
                if isinstance(message, int):
                    self.handleMessage(self.target_to_command_dictionary[message])
                elif message in c.ROBOT_MESSAGES:
                    self.handleMessage(message)
                elif isinstance(message, basestring):
                    return message
                else:
                    print("Unknown message in AbstractRobot: " + str(message))

    def updateVideo(self):
        if self.stream_enabled:
            new_bytes = self.robot.getVideoStreamBytes()
            if new_bytes is not None:
                self.bytes += new_bytes
                start = self.bytes.find('\xff\xd8')
                end = self.bytes.find('\xff\xd9')
                print len(self.bytes), start, end
                if start == -1 and end != -1:
                    self.bytes = self.bytes[end+2:]
                    return
                if start > end:
                    self.bytes = self.bytes[start:]
                    return
                if start != -1 and end != -1:
                    bytes_start_to_end = self.bytes[start:end+2]
                    self.bytes = self.bytes[end+2:]
                    self.sendImageToStreamingWindow(bytes_start_to_end)

    def sendImageToStreamingWindow(self, image):
        if self.psychopy_disabled is not None:
            if self.psychopy_disabled:
                self.window.updateStream(image)
            else:
                self.connection.sendMessage(image)