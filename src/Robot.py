import socket
import constants as c

import cv2
import urllib
import numpy as np
from PIL import Image, ImageTk
import Tkinter


class Robot(object):
    def __init__(self, connection):
        self.connection = connection
        """ @type : Connections.ConnectionProcessEnd.RobotConnection """
        self.socket = None
        self.stream = None
        self.bytes = None
        self.window = None
        self.image_label = None
        self.connection.waitMessages(self.start, self.exit, self.update, self.setup, self.sendMessage, poll=0)

    def start(self):
        while True:
            self.update()
            message = self.connection.receiveMessagePoll(0.3)
            if message is not None:
                if isinstance(message, basestring):
                    return message
                else:
                    self.sendMessage(message)

    def updateVideo(self):
        if self.stream is not None:
            self.bytes += self.stream.read(1024)
            a = self.bytes.find('\xff\xd8')
            b = self.bytes.find('\xff\xd9')
            if a != -1 and b != -1:
                jpg = self.bytes[a:b+2]
                self.bytes = self.bytes[b+2:]
                i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
                tki = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(i, cv2.COLOR_BGR2RGB)))
                self.image_label.configure(image=tki)
                self.image_label._backbuffer_ = tki  # avoid flicker caused by premature gc
                # cv2.imshow('i', i)

    def updateWindow(self):
        if self.window is not None:
            self.window.update()

    def update(self):
        self.updateVideo()
        self.updateWindow()

    def exit(self):
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

    def setup(self):
        options = self.connection.receiveMessageBlock()
        try:
            self.window = Tkinter.Tk()
            self.image_label = Tkinter.Label(self.window)
            self.image_label.pack()
            self.stream = urllib.urlopen("http://192.168.42.1:8080/?action=stream")
            self.bytes = ""
            return c.SUCCESS_MESSAGE
        except Exception, e:
            print("Error: " + str(e))
            return c.FAIL_MESSAGE
