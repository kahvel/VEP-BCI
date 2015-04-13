__author__ = 'Anti'

import Connections
import ConnectionPostOfficeEnd
import constants as c
import Plot
import PsdaExtraction


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
        raise NotImplementedError("addProcess not implemented!")


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
        raise NotImplementedError("addSingleProcess not implemented!")

    def addMultipleProcess(self):
        raise NotImplementedError("addMultipleProcess not implemented!")

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
        raise NotImplementedError("isSingleChannel not implemented!")


class TabConnection(Connections.MultipleConnections):
    def __init__(self, options_key):
        Connections.MultipleConnections.__init__(self)
        self.options_key = options_key

    def sendOptions(self, *options):
        options = options[0]
        for connection, option in zip(self.connections, options[self.options_key]):
            connection.sendOptions(option, options[c.DATA_FREQS])

    def setup(self, *options):
        options = options[0]
        self.close()
        while len(self.connections) < len(options[self.options_key]):
            self.addProcess()
        for connection, option in zip(self.connections, options[self.options_key]):
            connection.setup(option[c.DATA_METHODS], option[c.DATA_SENSORS], options)

    def addProcess(self):
        raise NotImplementedError("addProcess not implemented!")


class PlotTabConnection(TabConnection):
    def __init__(self):
        TabConnection.__init__(self, c.DATA_PLOTS)

    def addProcess(self):
        self.connections.append(PlotMethodConnection())


class ExtractionTabConnection(TabConnection):
    def __init__(self):
        TabConnection.__init__(self, c.DATA_EXTRACTION)

    def addProcess(self):
        self.connections.append(ExtractionMethodConnection())


class PlotMethodConnection(MethodConnection):
    def __init__(self):
        MethodConnection.__init__(self)

    def addProcess(self):
        self.connections.append(PlotSensorConnection())

    def isSingleChannel(self, method):
        return method == c.SUM_SIGNAL or method == c.SUM_AVG_SIGNAL

    def addSingleProcess(self):
        self.single_connections.append(ConnectionPostOfficeEnd.PlotConnection(Plot.MultipleChannel))

    def addMultipleProcess(self):
        self.multiple_connections.append(PlotSensorConnection())


class ExtractionMethodConnection(MethodConnection):
    def __init__(self):
        MethodConnection.__init__(self)

    def addProcess(self):
        self.connections.append(ExtractionSensorConnection())

    def isSingleChannel(self, method):
        return method == c.SUM_PSDA or method == c.SUM_BOTH

    def addSingleProcess(self):
        self.single_connections.append(ConnectionPostOfficeEnd.ExtractionConnection(PsdaExtraction.MultipleChannel))

    def addMultipleProcess(self):
        self.multiple_connections.append(ExtractionSensorConnection())


class PlotSensorConnection(SensorConnection):
    def __init__(self):
        SensorConnection.__init__(self)

    def addProcess(self):
        self.connections.append(ConnectionPostOfficeEnd.PlotConnection(Plot.SingleChannel))


class ExtractionSensorConnection(SensorConnection):
    def __init__(self):
        SensorConnection.__init__(self)

    def addProcess(self):
        self.connections.append(ConnectionPostOfficeEnd.ExtractionConnection(PsdaExtraction.SingleChannel))