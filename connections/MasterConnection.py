__author__ = 'Anti'

import Connections
import constants as c
import ConnectionPostOfficeEnd
import PlotConnection
import ExtractionConnection


class MasterConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)
        self.connections = {
            c.CONNECTION_EMOTIV:     ConnectionPostOfficeEnd.EmotivConnection(),
            c.CONNECTION_PSYCHOPY:   ConnectionPostOfficeEnd.PsychopyConnection(),
            c.CONNECTION_PLOT:       PlotConnection.PlotTabConnection(),
            c.CONNECTION_EXTRACTION: ExtractionConnection.ExtractionTabConnection()
            # c.CONNECTION_GAME:       ConnectionPostOfficeEnd.GameConnection()
        }

    def sendTargetMessage(self, message):
        self.connections[c.CONNECTION_PSYCHOPY].sendMessage(message)

    def receiveEmotivMessage(self):
        return self.connections[c.CONNECTION_EMOTIV].receiveMessagePoll(0.1)

    def sendPlotMessage(self, message):
        self.connections[c.CONNECTION_PLOT].sendMessage(message)

    def sendGameMessage(self, message):
        self.connections[c.CONNECTION_GAME].sendMessage(message)

    def sendExtractionMessage(self, message):
        self.connections[c.CONNECTION_EXTRACTION].sendMessage(message)

    def receiveExtractionMessage(self):
        return self.connections[c.CONNECTION_EXTRACTION].getMessages()

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
            if not self.connections[key].isClosed():
                self.connections[key].close()
