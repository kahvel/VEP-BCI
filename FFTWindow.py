__author__ = 'Anti'
import MyWindows
import Tkinter
import numpy as np
from scipy import signal
# import matplotlib.pyplot as plt


def scaleY(y, index, plot_count):
    return ((y*-30+50) + index*512 + 512/2) / plot_count


class AbstractFFTWindow(MyWindows.ToplevelWindow):
    def __init__(self, title):
        MyWindows.ToplevelWindow.__init__(self, title, 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.width = 512
        self.canvas.pack()
        self.continue_generating = True
        self.plot_count = 0
        self.sensor_names = []
        self.generators = []

    # def addGenCleanup(self):
    #     self.protocol("WM_DELETE_WINDOW", self.exit2)
    #
    # def removeGenCleanup(self):
    #     self.protocol("WM_DELETE_WINDOW", self.exit)
    #
    # def exit2(self):
    #     self.continue_generating = False


class FFTWindow(AbstractFFTWindow):
    def __init__(self):
        AbstractFFTWindow.__init__(self, "FFT")

    def setup(self, checkbox_values, sensor_names):
        self.plot_count = 0
        self.sensor_names = []
        # self.addGenCleanup()
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.sensor_names.append(sensor_names[i])
                self.generators.append(self.generator(self.plot_count))
                self.generators[self.plot_count].send(None)
                self.plot_count += 1

    def sendPacket(self, packet):
        for i in range(self.plot_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])

    def generator(self, index):
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
            line = self.canvas.create_line([i for i in enumerate(scaleY(np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates)))),index,self.plot_count))])
            self.canvas.update()


class AverageFFTWindow(AbstractFFTWindow):
    def __init__(self):
        AbstractFFTWindow.__init__(self, "Average FFT")

    def resetAverage(self, coordinates):
        for i in range(len(coordinates)):
            coordinates[i] = 0

    def setup(self, checkbox_values, sensor_names):
        self.plot_count = 0
        self.sensor_names = []
        # self.addGenCleanup()
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.sensor_names.append(sensor_names[i])
                self.generators.append(self.generator(self.plot_count))
                self.generators[self.plot_count].send(None)
                self.plot_count += 1

    def sendPacket(self, packet):
        for i in range(self.plot_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])

    def generator(self, index):
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
                if y == "Reset":
                    j = 0
                    self.resetAverage(average)
                    break
                coordinates[i] = y
            else:
                fft = np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates))))
                scaled_average = []
                for i in range(len(fft)):
                    average[i] = (average[i] * (j - 1) + fft[i]) / j
                    scaled_average.append(scaleY(average[i], index, self.plot_count))
                self.canvas.delete(line)
                line = self.canvas.create_line([i for i in enumerate(scaled_average)])
                self.canvas.update()
                continue
            self.canvas.delete(line)
            line = self.canvas.create_line(0, 0, 0, 0)


class AverageFFTWindow2(AbstractFFTWindow):
    def __init__(self):
        AbstractFFTWindow.__init__(self, "Average FFT")

    def resetAverage(self, coordinates):
        for i in range(len(coordinates)):
            coordinates[i] = 0

    def setup(self, checkbox_values, sensor_names):
        self.plot_count = 0
        self.sensor_names = []
        # self.addGenCleanup()
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.sensor_names.append(sensor_names[i])
                self.plot_count += 1
        self.generators.append(self.generator())
        self.generators[0].send(None)

    def sendPacket(self, packet):
        for i in range(self.plot_count):
            self.generators[0].send(packet.sensors[self.sensor_names[i]]["value"])

    def generator(self, index=0):
        coordinates = []
        for _ in range(self.plot_count):
            coordinates.append([0 for _ in range(1024)])
        average = [0 for _ in range(513)]
        line = self.canvas.create_line(0, 0, 0, 0)
        j = 0
        while True:
            j += 1
            for k in range(1024):
                for i in range(self.plot_count):
                    y = yield self.continue_generating  # Stopiteration exception
                    if not self.continue_generating:
                        return
                    if y == "Reset":
                        j = 0
                        self.resetAverage(average)
                        break
                    coordinates[i][k] = y
                else:
                    continue
                break
            else:
                ffts = []
                # print(coordinates)
                # x = np.fft.rfftfreq(len(coordinates))*128
                # y = np.fft.rfft(signal.detrend(coordinates))
                # plt.plot(x, y)
                # plt.show()
                for i in range(self.plot_count):
                    ffts.append(np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates[i])))))
                scaled_average = []
                for k in range(len(ffts[0])):
                    sum = 0
                    for i in range(self.plot_count):
                        sum += ffts[i][k]
                    average[k] = (average[k] * (j - 1) + sum/self.plot_count) / j
                    scaled_average.append(scaleY(average[k], index, 1))
                self.canvas.delete(line)
                line = self.canvas.create_line([i for i in enumerate(scaled_average)])
                self.canvas.update()
                continue
            self.canvas.delete(line)
            line = self.canvas.create_line(0, 0, 0, 0)