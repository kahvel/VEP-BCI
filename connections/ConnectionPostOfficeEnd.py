__author__ = 'Anti'

import Connections
import constants as c
import Main
import ConnectionProcessEnd
import multiprocessing


class AbstractConnection(Connections.AbstractConnection):
    def __init__(self):
        Connections.AbstractConnection.__init__(self)

    def setup(self, options):
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

    def setup(self, options=None):
        if self.connection is None:
            self.connection = self.newProcess()

    def newProcess(self):
        from_process, to_process = multiprocessing.Pipe()
        multiprocessing.Process(target=self.run_function, args=(self.connection_class(from_process),)).start()
        return to_process

    def isClosed(self):
        return self.connection is None

    def removeClosedConnections(self):
        pass


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

    def removeConnections(self, arg=None):
        connections = arg if arg is not None else self.connections
        for i in range(len(connections)-1, -1, -1):
            self.closeConnection(connections[i])
            del connections[i]

    def closeConnection(self, connection):
        connection.sendExitMessage()
        connection.receiveMessageBlock()

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

    def setup(self, options=None):
        if self.connection is None:
            self.connection = self.newProcess()


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

    def setup(self, sensors):
        self.removeConnections()
        while len(self.connections) < len(sensors):
            self.addProcess()
        for connection in self.connections:
            connection.setup()

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

    def setup(self, options):
        methods, sensors = options
        self.removeConnections()
        self.removeConnections(self.single_connections)
        self.removeConnections(self.multiple_connections)
        single_methods = [method for method in methods if "Sum" in method]
        multiple_method = [method for method in methods if "Sum" not in method]
        while len(self.single_connections) < len(single_methods):
            self.addSingleProcess()
        while len(self.multiple_connections) < len(multiple_method):
            self.addMultipleProcess()
        self.connections = self.single_connections+self.multiple_connections
        for connection in self.connections:
            connection.setup(sensors)


class MultiplePlotConnections(MultipleConnections):
    def __init__(self):
        MultipleConnections.__init__(self)

    def sendOptions(self, options):
        for connection, option in zip(self.connections, options[c.DATA_PLOTS]):
            connection.sendOptions((option, options[c.DATA_FREQS]))

    def setup(self, options):
        # freqs = options_arg[c.DATA_FREQS]
        # options = options_arg[c.DATA_PLOTS]
        self.removeConnections()
        while len(self.connections) < len(options[c.DATA_PLOTS]):
            self.addProcess()
        for connection, option in zip(self.connections, options[c.DATA_PLOTS]):
            connection.setup((option[c.DATA_METHODS], option[c.DATA_SENSORS]))

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
