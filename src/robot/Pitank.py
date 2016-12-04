import constants as c
import AbstractRobot

import socket
import urllib


class Pitank(AbstractRobot.AbstractRobot):
    def __init__(self, connection):
        AbstractRobot.AbstractRobot.__init__(self, connection)

    def getVideoStreamBytes(self):
        if self.stream is not None:
            return self.stream.read(1024)
        else:
            return None

    def handleMessage(self, message):
        if message in c.ROBOT_COMMANDS:
            self.sendRobotMessage(message)
        else:
            print("Unknown message in Robot: " + str(message))

    def sendRobotMessage(self, message):
        try:  # seems like PiTank closes the socket after receiving message
            robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            robot_socket.connect(("192.168.42.1", 12345))
            robot_socket.send(message)
        except Exception, e:
            print("Could not send message to PiTank. Is it switched on and computer connected to it?: " + str(e))

    def setupVideoStream(self):
        try:
            self.stream = urllib.urlopen("http://192.168.42.1:8080/?action=stream")
            self.bytes = ""
            return c.SUCCESS_MESSAGE
        except Exception, e:
            print("Error: " + str(e))
            return c.FAIL_MESSAGE
