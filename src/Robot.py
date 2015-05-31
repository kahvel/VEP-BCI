import constants as c
from gui.windows import VideoStream

import socket
import cv2
import urllib
import numpy as np


class Robot(object):
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

    def start(self):
        while True:
            self.update()
            message = self.connection.receiveMessageInstant()
            if message is not None:
                if isinstance(message, basestring):
                    return message
                else:
                    self.sendMessage(message)

    def updateVideo(self):
        if self.stream_enabled:
            if self.stream is not None:
                self.bytes += self.stream.read(1024)
                a = self.bytes.find('\xff\xd8')
                b = self.bytes.find('\xff\xd9')
                if a != -1 and b != -1:
                    jpg = self.bytes[a:b+2]
                    self.bytes = self.bytes[b+2:]
                    i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
                    if self.psychopy_disabled is not None:
                        if self.psychopy_disabled:
                            self.window.updateStream(i)
                        else:
                            self.connection.sendMessage(i)

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
        try:  # seems like PiTank closes the socket after receiving message
            robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            robot_socket.connect(("192.168.42.1", 12345))
            robot_socket.send(message)
        except Exception, e:
            print("Could not send message to robot (did you click setup? Is PiTank switched on and computer connected to PiTank?): " + str(e))

    def sendMessage(self, message):
        if message in c.ROBOT_COMMANDS:
            self.sendRobotMessage(message)
        else:
            print("Unknown message in Robot: " + str(message))

    def psychopyDisabled(self, options):
        return options[c.DISABLE] == 1

    def streamEnabled(self, options):
        return options[c.ROBOT_STREAM] == 1

    def setup(self):
        options = self.connection.receiveMessageBlock()
        self.exitWindow()
        self.stream_enabled = self.streamEnabled(options[c.DATA_ROBOT])
        if self.stream_enabled:
            self.psychopy_disabled = self.psychopyDisabled(options[c.DATA_BACKGROUND])
            if self.psychopy_disabled:
                self.window = VideoStream.StreamWindow()
                self.window.setup()
            else:
                self.window = None
        else:
            self.window = None
        try:
            self.stream = urllib.urlopen("http://192.168.42.1:8080/?action=stream")
            self.bytes = ""
            return c.SUCCESS_MESSAGE
        except Exception, e:
            print("Error: " + str(e))
            return c.FAIL_MESSAGE
