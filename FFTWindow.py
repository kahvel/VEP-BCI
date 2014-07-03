__author__ = 'Anti'
import MyWindows
import Tkinter
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


class FFTWindow(MyWindows.ToplevelWindow):
    def __init__(self):
        MyWindows.ToplevelWindow.__init__(self, "FFT", 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.width = 512
        self.canvas.pack()
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True

    def exit2(self):
        self.continue_generating = False

    def generator(self):
        count = 16
        x = 0
        coordinates = []
        line = self.canvas.create_line(0, 0, 0, 0)
        while True:
            for _ in range(count):
                y = yield self.continue_generating
                if not self.continue_generating:
                    break
                coordinates.append(y)
                x += 1
            if x > 1024:
                del coordinates[:count]
            self.canvas.delete(line)
            line = self.canvas.create_line([i for i in enumerate(np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates))))*-50+400)])
            self.canvas.update()


class AverageFFTWindow(MyWindows.ToplevelWindow):
    def __init__(self):
        MyWindows.ToplevelWindow.__init__(self, "Average FFT", 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.width = 512
        self.canvas.pack()
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True

    def exit2(self):
        self.continue_generating = False

    def generator(self): # Vale pidi!
        count = 1024
        average = [0 for _ in range(count)]
        line = self.canvas.create_line(0,0,0,0)
        j = 0
        while True:
            j += 1
            for i in range(count):
                y = yield self.continue_generating
                if not self.continue_generating:
                    break
                average[i] = (average[i] * (j - 1) + y) / j
            self.canvas.delete(line)
            line = self.canvas.create_line([i for i in enumerate(np.log10(np.abs(np.fft.rfft(average)))*-50+400)])
            self.canvas.update()

class AverageFFTWindow2(MyWindows.ToplevelWindow):
    def __init__(self):
        MyWindows.ToplevelWindow.__init__(self, "Average FFT", 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.width = 512
        self.canvas.pack()
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True

    def exit2(self):
        self.continue_generating = False

    def generator(self, plot_count):
        count = 1024
        coordinates = []
        for _ in range(plot_count):
            coordinates.append([0 for _ in range(1024)])
        line = self.canvas.create_line(0, 0, 0, 0)
        # j = 0
        while True:
            # j += 1
            for k in range(count):
                for i in range(plot_count):
                    y = yield self.continue_generating
                    if not self.continue_generating:
                        break
                    coordinates[i][k] = y
            ffts = []
            # print(coordinates)
            # x = np.fft.rfftfreq(len(coordinates))*128
            # y = np.fft.rfft(signal.detrend(coordinates))
            # plt.plot(x, y)
            # plt.show()
            for i in range(plot_count):
                ffts.append(np.log10(np.abs(np.fft.rfft(coordinates[i]))))
            final_average = []
            for k in range(512):
                sum = 0
                for i in range(plot_count):
                    sum += ffts[i][k]
                final_average.append(sum/plot_count*-50+400)
            self.canvas.delete(line)
            line = self.canvas.create_line([i for i in enumerate(final_average)])
            self.canvas.update()