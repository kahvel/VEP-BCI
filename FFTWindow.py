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
        self.channel_count = 0
        self.sensor_names = []
        self.generators = []
        self.update_after = 0

    # def addGenCleanup(self):
    #     self.protocol("WM_DELETE_WINDOW", self.exit2)
    #
    # def removeGenCleanup(self):
    #     self.protocol("WM_DELETE_WINDOW", self.exit)
    #
    # def exit2(self):
    #     self.continue_generating = False

    def setup(self, checkbox_values, sensor_names):
        self.channel_count = 0
        self.sensor_names = []
        self.generators = []
        # self.addGenCleanup()
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.sensor_names.append(sensor_names[i])
                self.channel_count += 1
        self.setPlotCount()
        for i in range(self.plot_count):
            self.generators.append(self.generator(i))
            self.generators[i].send(None)

    def generator(self, index):
        average_generator = self.gen()
        try:
            lines = [self.canvas.create_line(0, 0, 0, 0)]
            packet_count = 0
            delete = False
            average_generator.send(None)
            while True:
                y = yield
                avg = average_generator.send(y)
                if packet_count % self.update_after == 0 and packet_count != 0:
                    scaled_avg = self.scale(avg, index, packet_count)
                    lines.append(self.canvas.create_line(scaled_avg))
                    average_generator.next()
                    if True:
                        packet_count = 0
                        delete = True
                    if delete:
                        self.canvas.delete(lines[0])
                        del lines[0]
                    if index == self.plot_count-1:
                        self.canvas.update()
                packet_count += 1
        finally:
            print "closing average generator"
            average_generator.close()


class FFTWindow(AbstractFFTWindow):
    def __init__(self):
        AbstractFFTWindow.__init__(self, "FFT")
        self.update_after = 32

    def setPlotCount(self):
        self.plot_count = self.channel_count

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(len(coordinates)):
            result.append(i)
            result.append(scaleY(coordinates[i], index, self.plot_count))
        return result

    def gen(self):
        average = [0 for _ in range(1024)]
        yield
        while True:
            for i in range(32):
                for j in range(32):
                    y = yield
                    average[i*32+j] = y
                yield np.log10(np.abs(np.fft.rfft(signal.detrend(average))))


class AverageFFTWindow(AbstractFFTWindow):
    def __init__(self):
        AbstractFFTWindow.__init__(self, "Average FFT")
        self.update_after = 1024

    def setPlotCount(self):
        self.plot_count = self.channel_count

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(len(coordinates)):
            result.append(i)
            result.append(scaleY(coordinates[i], index, self.plot_count))
        return result

    def gen(self):
        average = [0 for _ in range(513)]
        coordinates = [0 for _ in range(1024)]
        k = 0
        yield
        while True:
            k += 1
            for i in range(1024):
                y = yield
                coordinates[i] = y
            fft = np.abs(np.fft.rfft(signal.detrend(coordinates)))
            for i in range(len(fft)):
                average[i] = (average[i] * (k - 1) + fft[i]) / k
            yield np.log10(average)


class AverageFFTWindow2(AbstractFFTWindow):
    def __init__(self):
        AbstractFFTWindow.__init__(self, "Average FFT")

    def setPlotCount(self):
        self.plot_count = 1
        self.update_after = self.channel_count*1024

    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[0].send(packet.sensors[self.sensor_names[i]]["value"])

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(len(coordinates)):
            result.append(i)
            result.append(scaleY(coordinates[i], index, self.plot_count))
        return result

    def gen(self):
        average = [0 for _ in range(513)]
        coordinates = []
        for _ in range(self.channel_count):
            coordinates.append([0 for _ in range(1024)])
        k = 0
        yield
        while True:
            k += 1
            for i in range(1024):
                for j in range(self.channel_count):
                    y = yield
                    coordinates[j][i] = y
            ffts = []
            for i in range(self.channel_count):
                ffts.append(np.abs(np.fft.rfft(signal.detrend(coordinates[i]))))
            for i in range(len(ffts[0])):
                sum = 0
                for j in range(self.channel_count):
                    sum += ffts[j][i]
                average[i] = (average[i] * (k - 1) + sum/self.channel_count) / k
            yield np.log10(average)