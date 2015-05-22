from generators import Plot

__author__ = 'Anti'

from connections import NotebookConnection, ConnectionPostOfficeEnd
import constants as c


class PlotTabConnection(NotebookConnection.TabConnection):
    def __init__(self):
        NotebookConnection.TabConnection.__init__(self, c.DATA_PLOTS)

    def getConnection(self):
        return PlotMethodConnection()


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
