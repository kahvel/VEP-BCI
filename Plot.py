__author__ = 'Anti'

import constants as c
import pyqtgraph as pg
from signal_processing import Signal, FFT


class Plot(object):
    def __init__(self, connection):
        self.connection = connection
        """ @type : ConnectionProcessEnd.PlotConnection """
        self.pw = None
        self.values = [0 for _ in range(100)]
        self.coordinates_generator = None
        self.button_key_to_class_key = {
            c.SIGNAL:         c.MULTIPLE_REGULAR,
            c.SUM_SIGNAL:     c.SINGLE_REGULAR,
            c.AVG_SIGNAL:     c.MULTIPLE_AVERAGE,
            c.SUM_AVG_SIGNAL: c.SINGLE_AVERAGE,
            c.POWER:          c.MULTIPLE_REGULAR,
            c.SUM_POWER:      c.SINGLE_REGULAR,
            c.AVG_POWER:      c.MULTIPLE_AVERAGE,
            c.SUM_AVG_POWER:  c.SINGLE_AVERAGE
        }
        self.want_to_exit = True
        self.single_generator = None
        self.sensor = None
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
                if self.single_generator:
                    for sensor in self.sensors:
                        coordinates = self.coordinates_generator.send(message.sensors[sensor]["value"])
                else:
                    coordinates = self.coordinates_generator.send(message.sensors[self.sensor]["value"])
                if coordinates is not None:
                    self.pw.plot(coordinates, clear=True)

    def setup(self):
        options, target_freqs = self.connection.receiveOptions()
        self.single_generator = self.isSingleGenerator(options)
        self.closeWindow()
        self.newWindow(self.getTitle(options))
        if c.DATA_SENSOR in options:
            self.sensor = options[c.DATA_SENSOR]
        self.sensors = options[c.DATA_SENSORS]
        self.setupGenerator(options)
        return c.SUCCESS_MESSAGE

    def setupGenerator(self, options):
        generator_class = self.getGeneratorClass(options)
        """ @type : Signal.Signal | FFT.FFT """
        generator_class.setup(options)
        self.coordinates_generator = generator_class.coordinates_generator()
        self.coordinates_generator.send(None)

    def getGeneratorClass(self, options):
        return getattr(
            Signal if self.isSignalPlot(options[c.DATA_METHOD]) else FFT,
            self.button_key_to_class_key[options[c.DATA_METHOD]]
        )()

    def isSignalPlot(self, method):
        return method in [c.SIGNAL, c.SUM_SIGNAL, c.AVG_SIGNAL, c.SUM_AVG_SIGNAL]

    def isSingleGenerator(self, options):
        return options[c.DATA_METHOD] == c.SUM_SIGNAL or options[c.DATA_METHOD] == c.SUM_AVG_SIGNAL

    def getTitle(self, options):
        print(options)
        if self.isSingleGenerator(options):
            return str(options[c.DATA_METHOD]) + " " + str(options[c.DATA_SENSORS])
        else:
            return str(options[c.DATA_METHOD]) + " " + str(options[c.DATA_SENSOR])

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
