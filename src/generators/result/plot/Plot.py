import pyqtgraph as pg

import constants as c
from generators import AbstractGenerator
from generators.coordinates import Signal, PSD
from generators.result import Logic


class Plot(AbstractGenerator.AbstractMyGenerator):
    def __init__(self, connection):
        AbstractGenerator.AbstractMyGenerator.__init__(self)
        self.connection = connection
        """ @type : ConnectionProcessEnd.PlotConnection """
        self.pw = None
        self.sensors = None
        self.options = None
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
                    coordinates = self.generator.send(message[sensor])
                if coordinates is not None:
                    self.updatePlot(coordinates)
                    self.generator.next()

    def updatePlot(self, coordinates):
        raise NotImplementedError("updatePlot not implemented!")

    def setup(self, options=None):
        self.options = self.connection.receiveOptions()
        self.sensors = self.options[c.DATA_SENSORS]
        AbstractGenerator.AbstractMyGenerator.setup(self, self.options)
        self.closeWindow()
        self.newWindow(self.getTitle(self.options))
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
            self.connection.close()
            self.closeWindow()
        else:
            event.ignore()


class SignalPlot(Plot):
    def __init__(self, connection):
        Plot.__init__(self, connection)

    def updatePlot(self, coordinates):
        self.pw.plot(coordinates, clear=True)


class PsdaPlot(Plot):
    def __init__(self, connection):
        """
        Superclass constructor call has to be last line, because it goes into waitMessages loop and never comes back.
        :param connection:
        :return:
        """
        self.target_freqs = None
        self.frequency_handler = Logic.InterpolationAndFftBins()
        Plot.__init__(self, connection)

    def setup(self, options=None):
        Plot.setup(self)
        self.frequency_handler.setup(self.options)
        self.target_freqs = sorted(self.options[c.DATA_FREQS].values())
        return c.SUCCESS_MESSAGE

    def updatePlot(self, coordinates):
        length = len(coordinates)
        frequency_bins = self.frequency_handler.getBins(length)
        self.pw.plot(frequency_bins, coordinates, clear=True)


class SumSignal(SignalPlot):
    def __init__(self, connection):
        SignalPlot.__init__(self, connection)

    def getGenerator(self, options):
        return Signal.SumSignal()


class NotSumSignal(SignalPlot):
    def __init__(self, connection):
        SignalPlot.__init__(self, connection)

    def getGenerator(self, options):
        return Signal.Signal()


class SumPower(PsdaPlot):
    def __init__(self, connection):
        PsdaPlot.__init__(self, connection)

    def getGenerator(self, options):
        return PSD.SumPsd()


class NotSumPower(PsdaPlot):
    def __init__(self, connection):
        PsdaPlot.__init__(self, connection)

    def getGenerator(self, options):
        return PSD.PSD()


class SumAvgSignal(SignalPlot):
    def __init__(self, connection):
        SignalPlot.__init__(self, connection)

    def getGenerator(self, options):
        return Signal.SumAverageSignal()


class NotSumAvgSignal(SignalPlot):
    def __init__(self, connection):
        SignalPlot.__init__(self, connection)

    def getGenerator(self, options):
        return Signal.AverageSignal()


class SumAvgPower(PsdaPlot):
    def __init__(self, connection):
        PsdaPlot.__init__(self, connection)

    def getGenerator(self, options):
        return PSD.SumAveragePSD()


class NotSumAvgPower(PsdaPlot):
    def __init__(self, connection):
        PsdaPlot.__init__(self, connection)

    def getGenerator(self, options):
        return PSD.AveragePSD()
