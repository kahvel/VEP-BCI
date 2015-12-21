import constants as c
import AbstractRobot

import socket
import urllib


class Pitank(AbstractRobot.AbstractRobot):
    def __init__(self, connection):
        AbstractRobot.AbstractRobot.__init__(self, connection)
        self.target_to_command_dictionary = None

    def getVideoStreamBytes(self):
        if self.stream is not None:
            return self.stream.read(1024)
        else:
            return None

    def handleMessage(self, message):
        if isinstance(message, int):
            self.sendMessage(self.target_to_command_dictionary[message])
            return True
        elif message in c.ROBOT_COMMANDS:
            self.sendMessage(message)
            return True
        else:
            return False

    def subclassSetup(self, options):
        self.target_to_command_dictionary = self.targetNumberToCommandDictionary(options[c.DATA_ROBOT])

    def targetNumberToCommandDictionary(self, options):
        return {
            options[c.ROBOT_OPTION_FORWARD]: c.MOVE_FORWARD,
            options[c.ROBOT_OPTION_BACKWARD]: c.MOVE_BACKWARD,
            options[c.ROBOT_OPTION_LEFT]: c.MOVE_LEFT,
            options[c.ROBOT_OPTION_RIGHT]: c.MOVE_RIGHT,
            options[c.ROBOT_OPTION_STOP]: c.MOVE_STOP
        }

    def sendRobotMessage(self, message):
        try:  # seems like PiTank closes the socket after receiving message
            robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            robot_socket.connect(("192.168.42.1", 12345))
            robot_socket.send(message)
        except Exception, e:
            print("Could not send message to robot (did you click setup? Is PiTank switched on and computer connected to PiTank?): " + str(e))

    def setupVideoStream(self):
        try:
            self.stream = urllib.urlopen("http://192.168.42.1:8080/?action=stream")
            self.bytes = ""
            return c.SUCCESS_MESSAGE
        except Exception, e:
            print("Error: " + str(e))
            return c.FAIL_MESSAGE
