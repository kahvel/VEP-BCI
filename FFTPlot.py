__author__ = 'Anti'
import PlotWindow
import numpy as np
from scipy import signal
# import matplotlib.pyplot as plt


class FFT(object):
    def __init__(self):
        self.window_function = 1

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(len(coordinates)):
            result.append(i)
            result.append(self.scaleY(coordinates[i], index, self.plot_count))
        return result

    def scaleY(self, y, index, plot_count):
        return ((y*-30+50) + index*512 + 512/2) / plot_count

    def setWindow(self, window_var, options_textboxes):
        length = 1024
        window_var = window_var.get()
        if window_var == "hanning":
            self.window_function = np.hanning(length)
        elif window_var == "hamming":
            self.window_function = np.hamming(length)
        elif window_var == "blackman":
            self.window_function = np.blackman(length)
        elif window_var == "kaiser":
            self.window_function = np.kaiser(length, float(options_textboxes["Beta"].get()))
        elif window_var == "bartlett":
            self.window_function = np.bartlett(length)
        elif window_var == "None":
            self.window_function = 1


class Multiple(object):
    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"])


class Single(object):
    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[0].send(packet.sensors[self.sensor_names[i]]["value"])


class Regular(object):
    pass


class Average(object):
    pass


class MultipleRegular(FFT, Regular, Multiple, PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self, "Multiple regular FFT plot")
        FFT.__init__(self)
        Regular.__init__(self)
        Multiple.__init__(self)

    def getGenerator(self, i):
        return self.plot_generator(i, 32, lambda x: True)

    def coordinates_generator(self):
        average = [0 for _ in range(1024)]
        yield
        while True:
            for i in range(32):
                for j in range(32):
                    y = yield
                    average[i*32+j] = y
                yield np.log10(np.abs(np.fft.rfft(signal.detrend(average))))


class MultipleAverage(FFT, Average, Multiple, PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self, "Multiple average FFT plot")
        FFT.__init__(self)
        Average.__init__(self)
        Multiple.__init__(self)

    def getGenerator(self, i):
        return self.plot_generator(i, 1024, lambda x: True)

    def coordinates_generator(self):
        average = [0 for _ in range(513)]
        coordinates = [0 for _ in range(1024)]
        k = 0
        yield
        while True:
            k += 1
            for i in range(1024):
                y = yield
                coordinates[i] = y
            fft = np.abs(np.fft.rfft(self.window_function*signal.detrend(coordinates)))
            for i in range(len(fft)):
                average[i] = (average[i] * (k - 1) + fft[i]) / k
            yield np.log10(average)


class SingleAverage(FFT, Average, Single, PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self, "Single average FFT plot")
        FFT.__init__(self)
        Average.__init__(self)
        Single.__init__(self)

    def getGenerator(self, i):
        return self.plot_generator(i, 1024*self.channel_count, lambda x: True)

    def coordinates_generator(self):
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
                ffts.append(np.abs(np.fft.rfft(self.window_function*signal.detrend(coordinates[i]))))
            for i in range(len(ffts[0])):
                sum = 0
                for j in range(self.channel_count):
                    sum += ffts[j][i]
                average[i] = (average[i] * (k - 1) + sum/self.channel_count) / k
            yield np.log10(average)


class SingleRegular(FFT, Regular, Single, PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self, "Single average FFT plot")
        FFT.__init__(self)
        Regular.__init__(self)
        Single.__init__(self)

    def getGenerator(self, i):
        return self.plot_generator(i, 1024*self.channel_count, lambda x: True)

    def coordinates_generator(self):
        average = [0 for _ in range(513)]
        coordinates = []
        for _ in range(self.channel_count):
            coordinates.append([0 for _ in range(1024)])
        yield
        while True:
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
                average[i] = sum/self.channel_count
            yield np.log10(average)