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
        raise NotImplementedError("setupPostOfficeEnd not implemented!")


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

    def addProcesses(self, options=None):
        if self.connection is None:
            self.connection = self.newProcess()

    def newProcess(self):
        from_process, to_process = multiprocessing.Pipe()
        multiprocessing.Process(target=self.run_function, args=(self.connection_class(from_process),)).start()
        return to_process

    def isClosed(self):
        return self.connection is None


class MultipleConnections(AbstractConnection):
    def __init__(self):
        AbstractConnection.__init__(self)
        self.connections = []
        """ @type : list[Connection] """
        self.methods_key = None

    def sendMessage(self, message):
        for connection in self.connections:
            connection.sendMessage(message)

    def receiveMessageInstant(self):
        return [connection.receiveMessageInstant() for connection in self.connections]

    def receiveMessagePoll(self, timeout):
        return [connection.receiveMessagePoll(timeout) for connection in self.connections]

    def receiveMessageBlock(self):
        return [connection.receiveMessageBlock() for connection in self.connections]

    def removeClosedConnections(self, connections):  # Is it necessary?
        for i in range(len(connections)-1, -1, -1):
            if connections[i] is None:
                del connections[i]

    # def sendOptions(self, options):
    #     for connection, option in zip(self.connections, options):
    #         connection.sendOptions(option)

    def isClosed(self):
        return all(connection.isClosed() for connection in self.connections)

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

    def sendOptions(self, options_tuple):
        self.sendMessage(options_tuple)


class MultipleExtractionConnections(MultipleConnections):
    def __init__(self):
        MultipleConnections.__init__(self, ExtractionConnection)

    # def sendOptions(self, options):
    #     for i, message in enumerate(options[c.DATA_EXTRACTION]):
    #         self.connections[i].sendMessage(message)
    #         self.connections[i].sendMessage(options[c.DATA_FREQS])


class Level2PlotConnection(MultipleConnections):
    def __init__(self):
        MultipleConnections.__init__(self)

    def sendOptions(self, options_tuple):
        options, freqs = options_tuple
        for connection, sensor in zip(self.connections, options[c.DATA_SENSORS]):
            options[c.DATA_SENSOR] = sensor
            connection.sendOptions((options, freqs))

    def addProcesses(self, sensors):
        self.removeClosedConnections(self.connections)
        while len(self.connections) < len(sensors):
            self.addProcess()
        for connection in self.connections:
            connection.addProcesses()

    def addProcess(self):
        self.connections.append(PlotConnection())


class Level3PlotConnection(MultipleConnections):
    def __init__(self):
        MultipleConnections.__init__(self)
        self.single_connections = []
        self.multiple_connections = []

    def sendOptions(self, options_tuple):
        options, freqs = options_tuple
        for connection, method in zip(self.connections, options[c.DATA_METHODS]):
            options[c.DATA_METHOD] = method
            connection.sendOptions((options, freqs))

    def addSingleProcess(self):
        self.single_connections.append(PlotConnection())

    def addMultipleProcess(self):
        self.multiple_connections.append(Level2PlotConnection())

    def addProcesses(self, options):
        methods, sensors = options
        self.removeClosedConnections(self.connections)
        self.removeClosedConnections(self.single_connections)
        self.removeClosedConnections(self.multiple_connections)
        for option in methods:
            if "Sum" in option:
                self.addSingleProcess()
            else:
                self.addMultipleProcess()
        self.connections = self.single_connections+self.multiple_connections
        for connection in self.connections:
            connection.addProcesses(sensors)


class MultiplePlotConnections(MultipleConnections):
    def __init__(self):
        MultipleConnections.__init__(self)

    def sendOptions(self, options):
        for connection, option in zip(self.connections, options[c.DATA_PLOTS]):
            connection.sendOptions((option, options[c.DATA_FREQS]))

    def addProcesses(self, options):
        # freqs = options_arg[c.DATA_FREQS]
        # options = options_arg[c.DATA_PLOTS]
        self.removeClosedConnections(self.connections)
        while len(self.connections) < len(options[c.DATA_PLOTS]):
            self.addProcess()
        for connection, option in zip(self.connections, options[c.DATA_PLOTS]):
            connection.addProcesses((option[c.DATA_METHODS], option[c.DATA_SENSORS]))

    def addProcess(self):
        self.connections.append(Level3PlotConnection())


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
