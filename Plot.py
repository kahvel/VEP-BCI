__author__ = 'Anti'

import constants as c
import pyqtgraph as pg


class Plot(object):
    def __init__(self, connection):
        self.connection = connection
        """ @type : ConnectionProcessEnd.PlotConnection """
        self.pw = pg.plot()
        self.values = [0 for _ in range(100)]
        self.connection.waitMessages(self.start, self.exit, self.updateWindow, self.setup)

    def start(self):
        i = 0
        while True:
            self.updateWindow()
            message = self.connection.receiveMessagePoll(0.1)
            if message is not None:
                print("Plot received: " + str(message))
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

    def updateWindow(self):
        pg.QtGui.QApplication.processEvents()

    def exit(self):
        self.connection.closeConnection()
        self.pw.close()
