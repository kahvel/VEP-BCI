__author__ = 'Anti'

import constants as c

#!/usr/bin/env python
# Plot a graph of Data which is comming in on the fly
# uses pylab
# Author: Norbert Feurle
# Date: 12.1.2012
# License: if you get any profit from this then please share it with me  and only use it for good

import pyqtgraph as pg


class Plot(object):
    def __init__(self, connection):
        self.connection = connection

        self.pw = pg.plot()

        self.values = [0 for _ in range(100)]



        print("Plot received: " + str(self.connection.recv()))
        print("Plot received: " + str(self.connection.recv()))
        print("Plot received: " + str(self.connection.recv()))
        self.loop()


    def updateData(self):
        if self.connection.poll():
            message = self.connection.recv().sensors["O1"]["value"]
            self.values.append(message)
            # if len(self.values) > 100:
            #     del self.values[0]
        self.root.after(5, self.updateData)

    def loop(self):
        i = 0
        while True:
            # if self.connection.poll(0.1):
            #     message = self.connection.recv()
            #     if message == c.START_MESSAGE:
            #         while True:
                        if self.connection.poll(0.007):
                            i += 1
                            message = self.connection.recv().sensors["O1"]["value"]
                            self.values.append(message)
                            if len(self.values) > 512:
                                del self.values[0]
                            if i % 10 == 0:
                                self.pw.plot(self.values, clear=True)
                                pg.QtGui.QApplication.processEvents()
                                i = 0

    def quit(self):
        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
                             # Fatal Python Error: PyEval_RestoreThread: NULL tstate
