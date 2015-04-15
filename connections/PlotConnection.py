__author__ = 'Anti'

import MultipleConnections
import ConnectionPostOfficeEnd
import constants as c
import Plot


class PlotTabConnection(MultipleConnections.TabConnection):
    def __init__(self):
        MultipleConnections.TabConnection.__init__(self, c.DATA_PLOTS)

    def addProcess(self):
        self.connections.append(PlotMethodConnection())


class PlotMethodConnection(MultipleConnections.MethodConnection):
    def __init__(self):
        MultipleConnections.MethodConnection.__init__(self)

    def addProcess(self, method):
        if method == c.SUM_SIGNAL:
            self.connections.append(ConnectionPostOfficeEnd.PlotConnection(Plot.SumSignal))
        elif method == c.SUM_POWER:
            self.connections.append(ConnectionPostOfficeEnd.PlotConnection(Plot.SumPower))
        elif method == c.SUM_AVG_SIGNAL:
            self.connections.append(ConnectionPostOfficeEnd.PlotConnection(Plot.SumAvgSignal))
        elif method == c.SUM_AVG_POWER:
            self.connections.append(ConnectionPostOfficeEnd.PlotConnection(Plot.SumAvgPower))
        elif method in [c.SIGNAL, c.POWER, c.AVG_SIGNAL, c.AVG_POWER]:
            self.connections.append(PlotSensorConnection())


class PlotSensorConnection(MultipleConnections.SensorConnection):
    def __init__(self):
        MultipleConnections.SensorConnection.__init__(self)

    def addProcess(self, method):
        if method == c.SIGNAL:
            self.connections.append(ConnectionPostOfficeEnd.PlotConnection(Plot.NotSumSignal))
        elif method == c.POWER:
            self.connections.append(ConnectionPostOfficeEnd.PlotConnection(Plot.NotSumPower))
        elif method == c.AVG_SIGNAL:
            self.connections.append(ConnectionPostOfficeEnd.PlotConnection(Plot.NotSumAvgSignal))
        elif method == c.AVG_POWER:
            self.connections.append(ConnectionPostOfficeEnd.PlotConnection(Plot.NotSumAvgPower))
