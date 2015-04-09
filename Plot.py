__author__ = 'Anti'

import constants as c
import pyqtgraph as pg
from signal_processing import Signal


class Plot(object):
    def __init__(self, connection):
        self.connection = connection
        """ @type : ConnectionProcessEnd.PlotConnection """
        self.pw = pg.plot()
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
        self.connection.waitMessages(self.start, self.exit, self.updateWindow, self.setup)

    def example(self, index):
        coordinates_generator = Signal.MultipleRegular()
        try:
            coordinates_generator.send(None)
            while True:
                y = yield
                coordinates = coordinates_generator.send(y)
                if coordinates is not None:
                    scaled_avg = self.scale(coordinates, index)
                    coordinates_generator.next()
        finally:
            print("Closing generator")
            coordinates_generator.close()

    def start(self):
        i = 0
        while True:
            self.updateWindow()
            message = self.connection.receiveMessagePoll(0.1)
            if message is not None:
                # print("Plot received: " + str(message))
                if isinstance(message, basestring):
                    return message
                else:
                    i += 1
                    message = message.sensors["O1"]["value"]
                    self.values.append(message)
                    if len(self.values) > 512:
                        del self.values[0]
                    if i % 10 == 0:
                        self.pw.plot(self.values, clear=True)
                        i = 0

    def setup(self):
        options, target_freqs = self.connection.receiveOptions()
        print("Plot options: ", options, target_freqs)
        # self.coordinates_generator = getattr(Signal, self.button_key_to_class_key[options[]])
        return c.SUCCESS_MESSAGE

    def updateWindow(self):
        pg.QtGui.QApplication.processEvents()

    def exit(self):
        self.connection.closeConnection()
        self.pw.close()
