__author__ = 'Anti'

import socket
import constants as c


class Robot(object):
    def __init__(self, connection):
        self.connection = connection
        """ @type : Connections.ConnectionProcessEnd.RobotConnection """
        self.socket = None
        self.connection.waitMessages(self.start, self.exit, lambda: None, self.setup)

    def start(self):
        pass

    def exit(self):
        pass

    def setup(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect(("192.168.42.1", 12345))
            # self.socket.settimeout(None)
            return c.SUCCESS_MESSAGE
        except:
            print("Failed to connect to robot!")
            return c.FAIL_MESSAGE
