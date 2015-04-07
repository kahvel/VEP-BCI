__author__ = 'Anti'

import constants as c


class AbstractConnection(object):
    def __init__(self):
        self.connection = None

    def sendMessage(self, message):
        raise NotImplementedError("sendMessage not implemented!")

    def sendStartMessage(self):
        self.sendMessage(c.START_MESSAGE)

    def sendStopMessage(self):
        self.sendMessage(c.STOP_MESSAGE)

    def sendExitMessage(self):
        self.sendMessage(c.EXIT_MESSAGE)

    def sendOptions(self, options):
        pass

    def receiveMessageInstant(self):
        if self.connection is not None:
            if self.connection.poll():  # If no timeout, returns immediately. If None, timeout is infinite.
                return self.receiveMessage()

    def receiveMessagePoll(self, timeout):
        if self.connection is not None:
            if self.connection.poll(timeout):
                return self.receiveMessage()

    def receiveMessageBlock(self):
        if self.connection is not None:
            if self.connection.poll(None):
                return self.receiveMessage()
            else:
                print("Warning! Infinite poll returned False.")

    def receiveMessage(self):
        raise NotImplementedError("receiveMessage not implemented!")
