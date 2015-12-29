from generators import Plot
from connections import ConnectionPostOfficeEnd, Connections
import constants as c

import copy


class PlotTabConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)

    def getConnection(self):
        return PlotMethodConnection()

    def setup(self, options):
        self.close()
        for tab_id, option in options[c.DATA_PLOTS].items():
            new_connection = self.getConnection()
            dict_copy = copy.deepcopy(option)
            dict_copy[c.DATA_FREQS] = options[c.DATA_FREQS]
            dict_copy[c.DATA_PROCESS_SHORT_SIGNAL] = options[c.DATA_PROCESS_SHORT_SIGNAL]
            new_connection.setup(dict_copy)
            new_connection.setId(tab_id)
            self.connections.append(new_connection)


class PlotMethodConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)

    def getConnection(self, method):
        if method == c.SUM_SIGNAL:
            return ConnectionPostOfficeEnd.PlotConnection(Plot.SumSignal)
        elif method == c.SUM_POWER:
            return ConnectionPostOfficeEnd.PlotConnection(Plot.SumPower)
        elif method == c.SUM_AVG_SIGNAL:
            return ConnectionPostOfficeEnd.PlotConnection(Plot.SumAvgSignal)
        elif method == c.SUM_AVG_POWER:
            return ConnectionPostOfficeEnd.PlotConnection(Plot.SumAvgPower)
        elif method in [c.SIGNAL, c.POWER, c.AVG_SIGNAL, c.AVG_POWER]:
            return PlotSensorConnection()
        else:
            raise ValueError("Illegal argument in getConnection: " + str(method))

    def setup(self, options):
        self.close()
        for method in options[c.DATA_METHODS]:
            new_connection = self.getConnection(method)
            dict_copy = copy.deepcopy(options)
            dict_copy[c.DATA_METHOD] = method
            new_connection.setup(dict_copy)
            new_connection.setId((method, tuple(options[c.DATA_SENSORS])))
            self.connections.append(new_connection)


class PlotSensorConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)

    def getConnection(self, method):
        if method == c.SIGNAL:
            return ConnectionPostOfficeEnd.PlotConnection(Plot.NotSumSignal)
        elif method == c.POWER:
            return ConnectionPostOfficeEnd.PlotConnection(Plot.NotSumPower)
        elif method == c.AVG_SIGNAL:
            return ConnectionPostOfficeEnd.PlotConnection(Plot.NotSumAvgSignal)
        elif method == c.AVG_POWER:
            return ConnectionPostOfficeEnd.PlotConnection(Plot.NotSumAvgPower)
        else:
            raise ValueError("Illegal argument in getConnection: " + str(method))

    def setup(self, options):
        self.close()
        for sensor in options[c.DATA_SENSORS]:
            new_connection = self.getConnection(options[c.DATA_METHOD])
            dict_copy = copy.deepcopy(options)
            dict_copy[c.DATA_SENSORS] = [sensor]
            new_connection.setup(dict_copy)
            new_connection.setId(sensor)
            self.connections.append(new_connection)
