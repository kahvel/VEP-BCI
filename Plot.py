__author__ = 'Anti'

import constants as c
import pyqtgraph as pg


class Plot(object):
    def __init__(self, connection):
        self.connection = connection
        """ @type : ConnectionProcessEnd.PlotConnection """
        self.pw = pg.plot()
        self.values = [0 for _ in range(100)]
        self.connection.waitMessages(self.loop, lambda: None, lambda: None)

    def loop(self):
        i = 0
        while True:
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
            pg.QtGui.QApplication.processEvents()

    def quit(self):
        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
                             # Fatal Python Error: PyEval_RestoreThread: NULL tstate
