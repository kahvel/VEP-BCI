__author__ = 'Anti'

import Connections
import constants as c
import Main
import ConnectionProcessEnd


class PsychopyConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, Main.runPsychopy, ConnectionProcessEnd.PsychopyConnection)

    def sendOptions(self, options):
        self.connection.send(options[c.DATA_BACKGROUND])
        self.connection.send(options[c.DATA_TARGETS])
        self.connection.send(options[c.DATA_TEST][c.TEST_STANDBY])

    def sendCurrentTarget(self, target):
        if target != 0:
            self.sendMessage(target)


class ExtractionConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, Main.runExtractionControl, ConnectionProcessEnd.ExtractionConnection)

    def sendOptions(self, options):
        self.connection.send(options)
        #self.connection.send(options[c.DATA_FREQS])


class PlotConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, Main.runPlotControl, ConnectionProcessEnd.PlotConnection)

    def sendOptions(self, *options_tuple):
        self.sendMessage(options_tuple)

    def setup(self, *options_other_end):
        if self.connection is None:
            self.connection = self.newProcess()


class MultipleExtractionConnections(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self, ExtractionConnection)

    # def sendOptions(self, options):
    #     for i, message in enumerate(options[c.DATA_EXTRACTION]):
    #         self.connections[i].sendMessage(message)
    #         self.connections[i].sendMessage(options[c.DATA_FREQS])


class Level2PlotConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)

    def sendOptions(self, *options_tuple):
        options, freqs = options_tuple
        for connection, sensor in zip(self.connections, options[c.DATA_SENSORS]):
            options[c.DATA_SENSOR] = sensor
            connection.sendOptions(options, freqs)

    def setup(self, *options):
        sensors, options_other_end = options
        self.close()
        while len(self.connections) < len(sensors):
            self.addProcess()
        for connection in self.connections:
            connection.setup(options_other_end)

    def addProcess(self):
        self.connections.append(PlotConnection())


class Level3PlotConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)
        self.single_connections = []
        self.multiple_connections = []

    def sendOptions(self, *options_tuple):
        options, freqs = options_tuple
        for connection, method in zip(self.connections, options[c.DATA_METHODS]):
            options[c.DATA_METHOD] = method
            connection.sendOptions(options, freqs)

    def addSingleProcess(self):
        self.single_connections.append(PlotConnection())

    def addMultipleProcess(self):
        self.multiple_connections.append(Level2PlotConnection())

    def setup(self, *options):
        methods, sensors, options_other_end = options
        self.close()
        self.close(self.single_connections)
        self.close(self.multiple_connections)
        single_methods = [method for method in methods if "Sum" in method]
        multiple_method = [method for method in methods if "Sum" not in method]
        while len(self.single_connections) < len(single_methods):
            self.addSingleProcess()
        while len(self.multiple_connections) < len(multiple_method):
            self.addMultipleProcess()
        self.connections = self.single_connections+self.multiple_connections
        for connection in self.connections:
            connection.setup(sensors, options_other_end)


class MultiplePlotConnections(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)

    def sendOptions(self, *options):
        options = options[0]
        for connection, option in zip(self.connections, options[c.DATA_PLOTS]):
            connection.sendOptions(option, options[c.DATA_FREQS])

    def setup(self, *options):
        options = options[0]
        self.close()
        while len(self.connections) < len(options[c.DATA_PLOTS]):
            self.addProcess()
        for connection, option in zip(self.connections, options[c.DATA_PLOTS]):
            connection.setup(option[c.DATA_METHODS], option[c.DATA_SENSORS], options)

    def addProcess(self):
        self.connections.append(Level3PlotConnection())


class GameConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, Main.runGame, ConnectionProcessEnd.GameConnection)

    def sendOptions(self, options):
        self.connection.send(options[c.DATA_FREQS])


class MainConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, Main.runMainWindow, ConnectionProcessEnd.MainConnection)
        self.connection = self.newProcess()


class EmotivConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, Main.runEmotiv, ConnectionProcessEnd.EmotivConnection)
        self.connection = self.newProcess()
