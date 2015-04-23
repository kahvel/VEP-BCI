__author__ = 'Anti'

import constants as c
import pyqtgraph as pg
from signal_processing import Signal, PSD


class Plot(object):
    def __init__(self, connection):
        self.connection = connection
        """ @type : ConnectionProcessEnd.PlotConnection """
        self.pw = None
        self.coordinates_generator = None
        self.sensors = None
        pg.QtGui.QMainWindow.closeEvent = self.exit
        self.connection.waitMessages(self.start, self.exit, self.updateWindow, self.setup)

    def start(self):
        while True:
            self.updateWindow()
            message = self.connection.receiveMessagePoll(0.1)
            if isinstance(message, basestring):
                return message
            if message is not None:
                for sensor in self.sensors:
                    coordinates = self.coordinates_generator.send(message.sensors[sensor]["value"])
                if coordinates is not None:
                    self.pw.plot(coordinates, clear=True)

    def setup(self):
        self.sensors, options, target_freqs = self.connection.receiveOptions()
        self.closeWindow()
        self.newWindow(self.getTitle(options))
        self.setupGenerator(options)
        return c.SUCCESS_MESSAGE

    def setupGenerator(self, options):
        self.coordinates_generator = self.getGenerator(options)
        """ @type : Signal.Signal | FFT.FFT """
        self.coordinates_generator.setup(options)

    def getGenerator(self, options):
        raise NotImplementedError("getGenerator not implemented!")

    def getTitle(self, options):
        raise NotImplementedError("getTitle not implemented!")

    def newWindow(self, title):
        self.pw = pg.plot(title=title)

    def updateWindow(self):
        pg.QtGui.QApplication.processEvents()

    def closeWindow(self):
        # if self.pw is not None:
        #     self.pw.close()
        #     self.pw = None
        pg.QtGui.QApplication.closeAllWindows()  # Also calls exit!!!

    def exit(self, event=None):
        if event is None:
            self.connection.closeConnection()
            self.closeWindow()
        else:
            event.ignore()


class NotSum(Plot):
    def __init__(self, connection):
        Plot.__init__(self, connection)

    def getTitle(self, options):
        return str(options[c.DATA_METHOD]) + " " + str(options[c.DATA_SENSOR])


class Sum(Plot):
    def __init__(self, connection):
        Plot.__init__(self, connection)

    def getTitle(self, options):
        return str(options[c.DATA_METHOD]) + " " + str(options[c.DATA_SENSORS])


class SumSignal(Sum):
    def __init__(self, connection):
        Sum.__init__(self, connection)

    def getGenerator(self, options):
        return Signal.SumSignal()


class NotSumSignal(NotSum):
    def __init__(self, connection):
        NotSum.__init__(self, connection)

    def getGenerator(self, options):
        return Signal.Signal()


class SumPower(Sum):
    def __init__(self, connection):
        Sum.__init__(self, connection)

    def getGenerator(self, options):
        return PSD.SumPsd()


class NotSumPower(NotSum):
    def __init__(self, connection):
        NotSum.__init__(self, connection)

    def getGenerator(self, options):
        return PSD.PSD()


class SumAvgSignal(Sum):
    def __init__(self, connection):
        Sum.__init__(self, connection)

    def getGenerator(self, options):
        return Signal.SumAverageSignal()


class NotSumAvgSignal(NotSum):
    def __init__(self, connection):
        NotSum.__init__(self, connection)

    def getGenerator(self, options):
        return Signal.AverageSignal()


class SumAvgPower(Sum):
    def __init__(self, connection):
        Sum.__init__(self, connection)

    def getGenerator(self, options):
        return PSD.SumAveragePSD()


class NotSumAvgPower(NotSum):
    def __init__(self, connection):
        NotSum.__init__(self, connection)

    def getGenerator(self, options):
        return PSD.AveragePSD()
