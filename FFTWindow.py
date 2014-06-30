__author__ = 'Anti'
from MyWindows import ToplevelWindow
from Tkinter import Canvas
import numpy as np
#import matplotlib.pyplot as plt

class FFTWindow(ToplevelWindow):
    def __init__(self):
        ToplevelWindow.__init__(self, "FFT", 512, 512)
        self.canvas = Canvas(self, width=512, height=512)
        self.width = 512
        self.canvas.pack()
        self.canvas.configure(xscrollincrement="1")
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True

    def exit2(self):
        self.continue_generating = False

    def generator(self):
        count = 16
        x=0
        list = []
        line = self.canvas.create_line(0,0,0,0)
        while x<1024:
            for _ in range(count):
                y = yield self.continue_generating
                if not self.continue_generating:
                    break
                list.append(y)
                x += 1
            self.canvas.delete(line)
            line = self.canvas.create_line([i for i in enumerate(np.log10(np.abs(np.fft.rfft(list)))*-100+400)])
            self.canvas.update()
        while True:
            for _ in range(count):
                y = yield self.continue_generating
                if not self.continue_generating:
                    break
                list.append(y)
            del list[:count]
            self.canvas.delete(line)
            line = self.canvas.create_line([i for i in enumerate(np.log10(np.abs(np.fft.rfft(list)))*-100+400)])
            self.canvas.update()
            # y = np.log10(np.abs(np.fft.rfft(list)))
            # plt.plot(y)
            # plt.show()


