__author__ = 'Anti'

import socket
import constants as c


class Robot(object):
    def __init__(self, connection):
        self.connection = connection
        """ @type : Connections.ConnectionProcessEnd.RobotConnection """
        self.socket = None
        self.connection.waitMessages(self.start, self.exit, lambda: None, self.setup, self.additional)

    def start(self):
        pass

    def exit(self):
        pass

    def sendMessage(self, message):
        try:
            self.socket.send(message)
        except Exception, e:
            print("Could not send message to robot: " + str(e))

    def additional(self, message):
        if message in c.ROBOT_COMMANDS:
            self.sendMessage(message)
            return True

    def setup(self):
        options = self.connection.receiveMessageBlock()
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1)
            self.socket.connect(("192.168.42.1", 12345))
            # self.socket.settimeout(None)
            return c.SUCCESS_MESSAGE
        except Exception, e:
            print("Failed to connect to robot! " + str(e))
            return c.FAIL_MESSAGE
