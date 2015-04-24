__author__ = 'Anti'

import constants as c
import pyqtgraph as pg
from generators import Signal, PSD, Generator


class Plot(Generator.AbstractMyGenerator):
    def __init__(self, connection):
        Generator.AbstractMyGenerator.__init__(self)
        self.connection = connection
        """ @type : ConnectionProcessEnd.PlotConnection """
        self.pw = None
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
                    coordinates = self.generator.send(message.sensors[sensor]["value"])
                if coordinates is not None:
                    self.pw.plot(coordinates, clear=True)
                    self.generator.next()

    def setup(self, options=None):
        options = self.connection.receiveOptions()
        self.sensors = options[c.DATA_SENSORS]
        Generator.AbstractMyGenerator.setup(self, options)
        self.closeWindow()
        self.newWindow(self.getTitle(options))
        return c.SUCCESS_MESSAGE

    def getTitle(self, options):
        return str(options[c.DATA_METHOD]) + " " + str(options[c.DATA_SENSORS])

    def newWindow(self, title):
        self.pw = pg.plot(title=title)

    def updateWindow(self):
        pg.QtGui.QApplication.processEvents()

    def closeWindow(self):
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


class Sum(Plot):
    def __init__(self, connection):
        Plot.__init__(self, connection)


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
