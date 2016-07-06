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


class PsdaPlot(Plot, Logic.TargetFrequencies):
    def __init__(self, connection):
        """
        Superclass constructor call has to be last line, because it goes into waitMessages loop and never comes back.
        :param connection:
        :return:
        """
        Logic.TargetFrequencies.__init__(self)
        self.fft_bin_handler = Logic.FftBins()
        self.target_magnitude_handler = Logic.TargetMagnitude()
        self.harmonics = None
        Plot.__init__(self, connection)

    def setup(self, options=None):
        message = Plot.setup(self)
        Logic.TargetFrequencies.setup(self, self.options)
        self.fft_bin_handler.setup(self.options)
        self.harmonics = [1, 2, 3]
        self.options[c.DATA_HARMONICS] = self.harmonics
        self.target_magnitude_handler.setup(self.options)
        return message

    def updateTargetMagnitudes(self, fft):
        target_magnitudes = self.target_magnitude_handler.getMagnitudesPerHarmonic(fft)
        for i, frequency in enumerate(self.frequencies):
            x = [frequency*harmonic for harmonic in self.harmonics]
            y = [target_magnitudes[harmonic][frequency] for harmonic in self.harmonics]
            self.pw.plot(x, y, pen=None, symbolBrush=(i, len(self.harmonics)), symbol='o')

    def updateLine(self, fft):
        length = len(fft)
        frequency_bins = self.fft_bin_handler.getBins(length)
        self.pw.plot(frequency_bins, fft, clear=True)

    def updatePlot(self, fft):
        self.updateLine(fft)
        self.updateTargetMagnitudes(fft)


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
