__author__ = 'Anti'

import Connections
import constants as c
import Main
import ConnectionProcessEnd
import multiprocessing


class AbstractConnection(Connections.AbstractConnection):
    def __init__(self):
        Connections.AbstractConnection.__init__(self)

    def addProcesses(self, n):
        raise NotImplementedError("addProcesses not implemented!")


class Connection(AbstractConnection):
    def __init__(self, run_function, connection_class):
        Connections.AbstractConnection.__init__(self)
        self.run_function = run_function
        self.connection_class = connection_class

    def sendMessage(self, message):
        self.connection.send(message)

    def receiveMessage(self):
        message = self.connection.recv()
        if message == c.CLOSE_MESSAGE:
            self.connection.close()
            self.connection = None
        return message

    def addProcesses(self, n=None):
        if self.connection is None:
            self.connection = self.newProcess()

    def newProcess(self):
        from_process, to_process = multiprocessing.Pipe()
        multiprocessing.Process(target=self.run_function, args=(self.connection_class(from_process),)).start()
        return to_process


class MultipleConnections(AbstractConnection):
    def __init__(self, connection_class):
        AbstractConnection.__init__(self)
        self.connections = []
        """ @type : list[Connection] """
        self.options_key = None
        self.connection_class = connection_class

    def sendMessage(self, message):
        for connection in self.connections:
            connection.sendMessage(message)

    def addProcess(self):
        self.connections.append(self.connection_class())

    def addProcesses(self, n):
        self.removeClosedConnections()
        while len(self.connections) < n:
            self.addProcess()
        for connection in self.connections:
            connection.addProcesses()

    def receiveMessageInstant(self):
        return [connection.receiveMessageInstant() for connection in self.connections]

    def receiveMessagePoll(self, timeout):
        return [connection.receiveMessagePoll(timeout) for connection in self.connections]

    def receiveMessageBlock(self):
        return [connection.receiveMessageBlock() for connection in self.connections]

    def removeClosedConnections(self):  # Is it necessary?
        for i in range(len(self.connections)-1, -1, -1):
            if self.connections[i] is None:
                del self.connections[i]

    def sendOptions(self, options):
        for connection, option in zip(self.connections, options):
            connection.sendOptions(option)

    # def getMessageInstant(self):
    #     return self.getMessage(lambda x: x.getMessageInstant())
    #
    # def getMessageBlock(self):
    #     return self.getMessage(lambda x: x.getMessageBlock())
    #
    # def getMessage(self, function):
    #     messages = []
    #     for i in range(len(self.connections)-1, -1, -1):
    #         message = function(self.connections[i])
    #         if message is not None:
    #             messages.append(message)
    #         elif self.connections[i] is None:  # If connection is None, it was closed by function(self.connections[i])
    #             del self.connections[i]
    #     return messages


class PsychopyConnection(Connection):
    def __init__(self):
        Connection.__init__(self, Main.runPsychopy, ConnectionProcessEnd.PsychopyConnection)

    def sendOptions(self, options):
        self.connection.send(options[c.DATA_BACKGROUND])
        self.connection.send(options[c.DATA_TARGETS])
        self.connection.send(options[c.DATA_TEST][c.TEST_STANDBY])

    def sendCurrentTarget(self, target):
        if target != 0:
            self.sendMessage(target)


class ExtractionConnection(Connection):
    def __init__(self):
        Connection.__init__(self, Main.runExtractionControl, ConnectionProcessEnd.ExtractionConnection)

    def sendOptions(self, options):
        self.connection.send(options)
        #self.connection.send(options[c.DATA_FREQS])


class PlotConnection(Connection):
    def __init__(self):
        Connection.__init__(self, Main.runPlotControl, ConnectionProcessEnd.PlotConnection)

    def sendOptions(self, options):
        pass
        # self.connection.sendMessage(options)
        # self.connection.sendMessage(options[c.DATA_FREQS])


class MultipleExtractionConnections(MultipleConnections):
    def __init__(self):
        MultipleConnections.__init__(self, ExtractionConnection)

    # def sendOptions(self, options):
    #     for i, message in enumerate(options[c.DATA_EXTRACTION]):
    #         self.connections[i].sendMessage(message)
    #         self.connections[i].sendMessage(options[c.DATA_FREQS])


class MultiplePlotConnections(MultipleConnections):
    def __init__(self):
        MultipleConnections.__init__(self, PlotConnection)

    # def sendOptions(self, options):
    #     for i, message in enumerate(options[c.DATA_PLOTS]):
    #         self.connections[i].sendMessage(message)
    #         self.connections[i].sendMessage(options[c.DATA_FREQS])


class GameConnection(Connection):
    def __init__(self):
        Connection.__init__(self, Main.runGame, ConnectionProcessEnd.GameConnection)

    def sendOptions(self, options):
        self.connection.send(options[c.DATA_FREQS])


class MainConnection(Connection):
    def __init__(self):
        Connection.__init__(self, Main.runMainWindow, ConnectionProcessEnd.MainConnection)
        self.connection = self.newProcess()


class EmotivConnection(Connection):
    def __init__(self):
        Connection.__init__(self, Main.runEmotiv, ConnectionProcessEnd.EmotivConnection)
        self.connection = self.newProcess()
