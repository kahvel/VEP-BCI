__author__ = 'Anti'

import Connections
import constants as c
import ConnectionPostOfficeEnd
import PlotConnection


class MasterConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)
        self.connections = {
            c.CONNECTION_EMOTIV:     ConnectionPostOfficeEnd.EmotivConnection(),
            c.CONNECTION_PSYCHOPY:   ConnectionPostOfficeEnd.PsychopyConnection(),
            c.CONNECTION_EXTRACTION: PlotConnection.PlotTabConnection(),
            c.CONNECTION_PLOT:       PlotConnection.ExtractionTabConnection()
            # c.CONNECTION_GAME:       ConnectionPostOfficeEnd.GameConnection()
        }

    def sendCurrentTarget(self, target):
        self.connections[c.CONNECTION_PSYCHOPY].sendCurrentTarget(target)

    def receiveEmotivMessage(self):
        return self.connections[c.CONNECTION_EMOTIV].receiveMessagePoll(0.1)

    def sendPlotMessage(self, message):
        self.connections[c.CONNECTION_PLOT].sendMessage(message)

    def sendExtractionMessage(self, message):
        self.connections[c.CONNECTION_EXTRACTION].sendMessage(message)

    def sendStartMessage(self):
        for key in self.connections:
            self.connections[key].sendStartMessage()

    def sendStopMessage(self):
        for key in self.connections:
            self.connections[key].sendStopMessage()

    def sendSetupMessage(self):
        for key in self.connections:
            self.connections[key].sendSetupMessage()

    def sendOptions(self, options):
        for key in self.connections:
            self.connections[key].sendOptions(options)

    def setup(self, options):
        for key in self.connections:
            self.connections[key].setup(options)

    def setupSuccessful(self):
        for key in self.connections:
            if not self.connections[key].setupSuccessful():
                return False
        return True

    def close(self, arg=None):
        for key in self.connections:
            # if not self.connections[key].isClosed():
            self.connections[key].close()

    def setupOtherEnd(self, options):
        self.sendSetupMessage()
        self.sendOptions(options)
        # for key in self.connections:
        #     self.connections[key].sendSetupMessage()
        #     self.connections[key].sendOptions()
        #     if not self.connections[key].setupSuccessful():
        #         return c.FAIL_MESSAGE
        #     # while True:
        #     #     message = self.connections[key].receiveMessageBlock()
        #     #     print(key, message)
        #     #     if message == c.FAIL_MESSAGE:
        #     #         return message
        #     #     elif message == c.SUCCESS_MESSAGE:
        #     #         break
        # return c.SUCCESS_MESSAGE