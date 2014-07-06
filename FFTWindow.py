__author__ = 'Anti'
import MyWindows
import Tkinter
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


def scaleY(y, index, plot_count):
    return ((y*-30+50) + index*512 + 512/2) / plot_count


class AbstractFFTWindow(MyWindows.ToplevelWindow):
    def __init__(self, title):
        MyWindows.ToplevelWindow.__init__(self, title, 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.width = 512
        self.canvas.pack()
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True

    def exit2(self):
        self.continue_generating = False


class FFTWindow(AbstractFFTWindow):
    def __init__(self):
        AbstractFFTWindow.__init__(self, "FFT")

    def generator(self, index, plot_count):
        count = 16
        x = 0
        coordinates = []
        line = self.canvas.create_line(0, 0, 0, 0)
        while True:
            for _ in range(count):
                y = yield self.continue_generating
                if not self.continue_generating:
                    return
                coordinates.append(y)
                x += 1
            if x > 1024:
                del coordinates[:count]
            self.canvas.delete(line)
            line = self.canvas.create_line([i for i in enumerate(scaleY(np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates)))),index,plot_count))])
            self.canvas.update()


class AverageFFTWindow(AbstractFFTWindow):
    def __init__(self):
        AbstractFFTWindow.__init__(self, "Average FFT")

    def generator(self, index, plot_count):
        coordinates = [0 for _ in range(1024)]
        average = [0 for _ in range(513)]
        line = self.canvas.create_line(0, 0, 0, 0)
        j = 0
        while True:
            j += 1
            for i in range(1024):
                y = yield self.continue_generating
                if not self.continue_generating:
                    return
                coordinates[i] = y
            fft = np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates))))
            scaled_average = []
            for i in range(len(fft)):
                average[i] = (average[i] * (j - 1) + fft[i]) / j
                scaled_average.append(scaleY(average[i], index, plot_count))
            self.canvas.delete(line)
            line = self.canvas.create_line([i for i in enumerate(scaled_average)])
            self.canvas.update()


class AverageFFTWindow2(AbstractFFTWindow):
    def __init__(self):
        AbstractFFTWindow.__init__(self, "Average FFT")

    def generator(self, plot_count):
        coordinates = []
        for _ in range(plot_count):
            coordinates.append([0 for _ in range(1024)])
        average = [0 for _ in range(513)]
        line = self.canvas.create_line(0, 0, 0, 0)
        j = 0
        while True:
            j += 1
            for k in range(1024):
                for i in range(plot_count):
                    y = yield self.continue_generating  # Stopiteration exception
                    if not self.continue_generating:
                        return
                    coordinates[i][k] = y
            ffts = []
            # print(coordinates)
            # x = np.fft.rfftfreq(len(coordinates))*128
            # y = np.fft.rfft(signal.detrend(coordinates))
            # plt.plot(x, y)
            # plt.show()
            for i in range(plot_count):
                ffts.append(np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates[i])))))
            scaled_average = []
            for k in range(len(ffts[0])):
                sum = 0
                for i in range(plot_count):
                    sum += ffts[i][k]
                average[k] = (average[k] * (j - 1) + sum/plot_count) / j
                scaled_average.append(scaleY(average[k], 0, 1))
            self.canvas.delete(line)
            line = self.canvas.create_line([i for i in enumerate(scaled_average)])
            self.canvas.update()