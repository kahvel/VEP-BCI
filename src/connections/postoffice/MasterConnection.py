from connections import Connections
from connections.postoffice import ConnectionPostOfficeEnd
from connections.postoffice import PlotConnection
from connections.postoffice import ExtractionConnection

import constants as c


class MasterConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)
        self.connections = {
            c.CONNECTION_EMOTIV:     ConnectionPostOfficeEnd.EmotivConnection(),
            c.CONNECTION_PSYCHOPY:   ConnectionPostOfficeEnd.PsychopyConnection(),
            c.CONNECTION_PLOT:       PlotConnection.PlotTabConnection(),
            c.CONNECTION_EXTRACTION: ExtractionConnection.ExtractionTabConnection(),
            c.CONNECTION_ROBOT:      ConnectionPostOfficeEnd.RobotConnection()
        }
        self.connection_to_data = {
            c.CONNECTION_EMOTIV:     c.DATA_EMOTIV,
            c.CONNECTION_PSYCHOPY:   c.DATA_BACKGROUND,
            c.CONNECTION_PLOT:       c.DATA_PLOTS,
            c.CONNECTION_EXTRACTION: c.DATA_EXTRACTION,
            c.CONNECTION_ROBOT:      c.DATA_ROBOT
        }

    def sendRobotMessage(self, message):
        if not self.connections[c.CONNECTION_ROBOT].isClosed():
            self.connections[c.CONNECTION_ROBOT].sendMessage(message)
        else:
            print("Robot connection is closed. Did you click setup?")

    def sendTargetMessage(self, message):
        self.connections[c.CONNECTION_PSYCHOPY].sendMessage(message)

    def receiveEmotivMessage(self):
        return self.connections[c.CONNECTION_EMOTIV].receiveMessagePoll(0.01)

    def receiveRobotMessage(self):
        return self.connections[c.CONNECTION_ROBOT].receiveMessageInstant()

    def sendPlotMessage(self, message):
        self.connections[c.CONNECTION_PLOT].sendMessage(message)

    def sendExtractionMessage(self, message):
        self.connections[c.CONNECTION_EXTRACTION].sendMessage(message)

    def sendClearBuffersMessage(self):
        self.connections[c.CONNECTION_EXTRACTION].sendMessage(c.CLEAR_BUFFER_MESSAGE)

    def receiveExtractionMessage(self):
        return self.connections[c.CONNECTION_EXTRACTION].getMessages()

    def sendMessage(self, message):
        for key in self.connections:
            self.connections[key].sendMessage(message)

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
            if key == c.CONNECTION_EXTRACTION or key == c.CONNECTION_PLOT or\
                    not options[self.connection_to_data[key]][c.DISABLE]:
                self.connections[key].setup(options)
            else:
                self.connections[key].close()

    def setupSuccessful(self):
        result = True
        for key in self.connections:
            if not self.connections[key].setupSuccessful():
                result = False
        return result

    def close(self, arg=None):
        for key in self.connections:
            if not self.connections[key].isClosed():
                self.connections[key].close()
