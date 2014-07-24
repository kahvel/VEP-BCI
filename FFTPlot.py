__author__ = 'Anti'
import PlotWindow
import numpy as np
from scipy import signal
# import matplotlib.pyplot as plt


class FFT(object):
    def __init__(self):
        self.window_function = 1
        self.length = 512
        self.step = 32

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(len(coordinates)):
            result.append(i*512/len(coordinates))
            result.append(self.scaleY(coordinates[i], index, self.plot_count))
        return result

    def scaleY(self, y, index, plot_count):
        return ((y*-30+50) + index*512 + 512/2) / plot_count

    def setOptions(self, window_var, options_textboxes):
        self.length = int(options_textboxes["Length"].get())
        self.step = int(options_textboxes["Step"].get())
        window_var = window_var.get()
        if window_var == "hanning":
            self.window_function = np.hanning(self.length)
        elif window_var == "hamming":
            self.window_function = np.hamming(self.length)
        elif window_var == "blackman":
            self.window_function = np.blackman(self.length)
        elif window_var == "kaiser":
            self.window_function = np.kaiser(self.length, float(options_textboxes["Beta"].get()))
        elif window_var == "bartlett":
            self.window_function = np.bartlett(self.length)
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
        return self.plot_generator(i, self.step, lambda x: True)

    def coordinates_generator(self):
        coordinates = [0 for _ in range(self.length)]
        yield
        while True:
            for i in range(self.length/self.step):
                for j in range(self.step):
                    y = yield
                    coordinates[i*self.step+j] = y
                yield np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates))))


class MultipleAverage(FFT, Average, Multiple, PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self, "Multiple average FFT plot")
        FFT.__init__(self)
        Average.__init__(self)
        Multiple.__init__(self)

    def getGenerator(self, i):
        return self.plot_generator(i, self.step, lambda x: True)

    def coordinates_generator(self):
        average = [0 for _ in range(self.length//2+1)]
        coordinates = [0 for _ in range(self.length)]
        k = 0
        reset_average = True
        yield
        while True:
            for i in range(self.length/self.step):
                for j in range(self.step):
                    y = yield
                    coordinates[i*self.step+j] = y
                if reset_average:
                    k = 0
                    average = [0 for _ in range(self.length//2+1)]
                k += 1
                fft = np.abs(np.fft.rfft(self.window_function*signal.detrend(coordinates)))
                for i in range(len(fft)):
                    average[i] = (average[i] * (k - 1) + fft[i]) / k
                yield np.log10(average)
            reset_average = False


class SingleAverage(FFT, Average, Single, PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self, "Single average FFT plot")
        FFT.__init__(self)
        Average.__init__(self)
        Single.__init__(self)

    def getGenerator(self, i):
        return self.plot_generator(i, self.length*self.channel_count, lambda x: True)

    def coordinates_generator(self):
        average = [0 for _ in range(self.length//2+1)]
        coordinates = []
        for _ in range(self.channel_count):
            coordinates.append([0 for _ in range(self.length)])
        k = 0
        reset_average = True
        yield
        while True:
            for i in range(self.length/self.step):
                for j in range(self.step):
                    for channel in range(self.channel_count):
                        y = yield
                        coordinates[channel][i*self.step+j] = y
                if reset_average:
                    k = 0
                    average = [0 for _ in range(self.length//2+1)]
                k += 1
                ffts = []
                for i in range(self.channel_count):
                    ffts.append(np.abs(np.fft.rfft(self.window_function*signal.detrend(coordinates[i]))))
                for i in range(len(ffts[0])):
                    sum = 0
                    for j in range(self.channel_count):
                        sum += ffts[j][i]
                    average[i] = (average[i] * (k - 1) + sum/self.channel_count) / k
                yield np.log10(average)
            reset_average = False


class SingleRegular(FFT, Regular, Single, PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self, "Single average FFT plot")
        FFT.__init__(self)
        Regular.__init__(self)
        Single.__init__(self)

    def getGenerator(self, i):
        return self.plot_generator(i, self.length*self.channel_count, lambda x: True)

    def coordinates_generator(self):
        average = [0 for _ in range(self.length//2+1)]
        coordinates = []
        for _ in range(self.channel_count):
            coordinates.append([0 for _ in range(self.length)])
        reset_average = True
        yield
        while True:
            for i in range(self.length/self.step):
                for j in range(self.step):
                    for channel in range(self.channel_count):
                        y = yield
                        coordinates[channel][i*self.step+j] = y
                if reset_average:
                    average = [0 for _ in range(self.length//2+1)]
                ffts = []
                for i in range(self.channel_count):
                    ffts.append(np.abs(np.fft.rfft(signal.detrend(coordinates[i]))))
                for i in range(len(ffts[0])):
                    sum = 0
                    for j in range(self.channel_count):
                        sum += ffts[j][i]
                    average[i] = sum/self.channel_count
                yield np.log10(average)
            reset_average = False