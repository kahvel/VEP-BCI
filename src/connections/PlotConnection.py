from generators import Plot
from connections import NotebookConnection, ConnectionPostOfficeEnd, Connections
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
            new_connection.setup(dict_copy)
            new_connection.setId(tab_id)
            self.connections.append(new_connection)


class PlotMethodConnection(NotebookConnection.MethodConnection):
    def __init__(self):
        NotebookConnection.MethodConnection.__init__(self)

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


class PlotSensorConnection(NotebookConnection.SensorConnection):
    def __init__(self):
        NotebookConnection.SensorConnection.__init__(self)

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
