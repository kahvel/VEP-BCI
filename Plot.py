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
        self.close_connections = True
        self.multiple_channels = None
        self.sensor = None
        self.sensors = None
        pg.QtGui.QMainWindow.closeEvent = self.exit
        self.connection.waitMessages(self.start, lambda: self.exit(None), self.updateWindow, self.setup)

    def start(self):
        while True:
            self.updateWindow()
            message = self.connection.receiveMessagePoll(0.1)
            if isinstance(message, basestring):
                return message
            if message is not None:
                if self.multiple_channels:
                    for sensor in self.sensors:
                        coordinates = self.coordinates_generator.send(message.sensors[sensor]["value"])
                else:
                    coordinates = self.coordinates_generator.send(message.sensors[self.sensor]["value"])
                # scale?
                if coordinates is not None:
                    self.pw.plot(coordinates, clear=True)

    def setup(self):
        self.closeWindow()
        self.newWindow()
        options, target_freqs = self.connection.receiveOptions()
        self.multiple_channels = "Sum" in options[c.DATA_METHOD]
        if c.DATA_SENSOR in options:
            self.sensor = options[c.DATA_SENSOR]
        self.sensors = options[c.DATA_SENSORS]
        self.setupGenerator(options)
        return c.SUCCESS_MESSAGE

    def setupGenerator(self, options):
        generator_class = getattr(
            Signal if "signal" in options[c.DATA_METHOD].lower() else FFT,
            self.button_key_to_class_key[options[c.DATA_METHOD]]
        )()
        """ @type : Signal.Signal | FFT.FFT """
        generator_class.setup(options)
        self.coordinates_generator = generator_class.coordinates_generator()
        self.coordinates_generator.send(None)

    def newWindow(self):
        self.pw = pg.plot()

    def updateWindow(self):
        pg.QtGui.QApplication.processEvents()

    def closeWindow(self):
        if self.pw is not None:
            self.pw.close()
            self.pw = None
            self.close_connections = False
            pg.QtGui.QApplication.closeAllWindows()  # Also calls closeEvent!!!
            self.close_connections = True

    def exit(self, event):
        if self.close_connections:
            self.connection.closeConnection()
            self.closeWindow()
