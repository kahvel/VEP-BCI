__author__ = 'Anti'

import Connections
import ConnectionPostOfficeEnd
import constants as c
import Plot


class SensorConnection(Connections.MultipleConnections):
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
        self.connections.append(ConnectionPostOfficeEnd.PlotConnection(Plot.SingleChannelPlot))


class MethodConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)
        self.single_connections = []
        self.multiple_connections = []
        self.single_methods = []
        self.multiple_methods = []

    def sendOptions(self, *options_tuple):
        options, freqs = options_tuple
        for connection, method in zip(self.single_connections, self.single_methods):
            options[c.DATA_METHOD] = method
            connection.sendOptions(options, freqs)
        for connection, method in zip(self.multiple_connections, self.multiple_methods):
            options[c.DATA_METHOD] = method
            connection.sendOptions(options, freqs)

    def addSingleProcess(self):
        self.single_connections.append(ConnectionPostOfficeEnd.PlotConnection(Plot.MultipleChannelPlot))

    def addMultipleProcess(self):
        self.multiple_connections.append(SensorConnection())

    def setup(self, *options):
        methods, sensors, options_other_end = options
        self.close()
        self.close(self.single_connections)
        self.close(self.multiple_connections)
        self.single_methods = [method for method in methods if self.isSingleChannel(method)]
        self.multiple_methods = [method for method in methods if not self.isSingleChannel(method)]
        while len(self.single_connections) < len(self.single_methods):
            self.addSingleProcess()
        while len(self.multiple_connections) < len(self.multiple_methods):
            self.addMultipleProcess()
        self.connections = self.single_connections+self.multiple_connections
        for connection in self.connections:
            connection.setup(sensors, options_other_end)

    def isSingleChannel(self, method):
        return method == c.SUM_SIGNAL or method == c.SUM_AVG_SIGNAL


class TabConnection(Connections.MultipleConnections):
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
        self.connections.append(MethodConnection())