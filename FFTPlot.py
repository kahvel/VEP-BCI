__author__ = 'Anti'
import PlotWindow
import numpy as np
import scipy.signal
# import matplotlib.pyplot as plt


class FFT(object):
    def __init__(self):
        self.start_deleting = lambda x: True

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(len(coordinates)):
            result.append(i*self.window_length/len(coordinates))
            result.append(self.scaleY(coordinates[i], index, self.plot_count))
        return result

    def scaleY(self, y,  index, plot_count):
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        return ((((y - self.min_packet[index]) * (-100 - 100)) / (self.max_packet[index] - self.min_packet[index])) + 100
                + index*self.window_height + self.window_height/2) / plot_count

    def normaliseSpectrum(self, fft):
        if self.normalise:
            return fft/sum(fft)
        else:
            return np.log10(fft)

    def filterPrevState(self, prev_coordinates):
        if self.filter:
            return scipy.signal.lfiltic(1.0, self.filter_coefficients, prev_coordinates)
        else:
            return None

    def setInitSignal(self, min_packet, max_packet, averages, init_coordinates, prev_coordinates):
        self.averages = averages
        self.init_coordinates = init_coordinates[:]
        self.prev_coordinates = prev_coordinates[:]
        self.min_packet = []
        self.max_packet = []
        self.signal_min_packet = min_packet
        self.signal_max_packet = max_packet
        for i in range(len(init_coordinates)):
            spectrum = self.normaliseSpectrum(self.signalPipeline(init_coordinates[i], prev_coordinates[i]))[1:]
            self.min_packet.append(min(spectrum))
            self.max_packet.append(max(spectrum))

    def scaleSignal(self, coordinates, index, packet_count):
        result = []
        for i in range(len(coordinates)):
            result.append(i*self.window_length/len(coordinates))
            result.append(self.scaleSignalY(coordinates[i], index, self.plot_count))
        return result

    def scaleSignalY(self, y,  index, plot_count):
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        return ((((y - self.signal_min_packet[index]) * (-100 - 100)) / (self.signal_max_packet[index] - self.signal_min_packet[index])) + 100
                + index*self.window_height + self.window_height/2) / plot_count

    def signalPipeline(self, coordinates, prev_coordinates):
        detrended_signal = scipy.signal.detrend(coordinates)
        self.prev_filter = self.filterPrevState(prev_coordinates)
        filtered_signal = self.filterSignal(detrended_signal)
        windowed_signal = self.windowSignal(filtered_signal, self.window_function)
        # self.canvas.delete(self.line)
        # self.line = self.canvas.create_line(self.scaleSignal(windowed_signal, 0, 1), fill="Red")
        amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
        return amplitude_spectrum


class Multiple(object):
    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(packet.sensors[self.sensor_names[i]]["value"]-self.averages[i])


class Single(object):
    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[0].send(packet.sensors[self.sensor_names[i]]["value"]-self.averages[i])


class Regular(object):
    pass


class Average(object):
    pass


class MultipleRegular(FFT, Regular, Multiple, PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self, "Multiple regular FFT plot")
        self.line = self.canvas.create_line(0,0,0,0)
        FFT.__init__(self)
        Regular.__init__(self)
        Multiple.__init__(self)

    def coordinates_generator(self, index):
        yield
        coordinates = self.init_coordinates[index]
        prev_coordinates = self.prev_coordinates[index]
        while True:
            for i in range(self.length/self.step):
                self.prev_coordinates.extend(coordinates[:self.step])
                del self.prev_coordinates[:self.step]
                del coordinates[:self.step]
                for j in range(self.step):
                    y = yield
                    coordinates.append(y)
                spectrum = self.signalPipeline(coordinates, prev_coordinates)
                yield self.normaliseSpectrum(spectrum)


class MultipleAverage(FFT, Average, Multiple, PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self, "Multiple average FFT plot")
        FFT.__init__(self)
        Average.__init__(self)
        Multiple.__init__(self)

    def coordinates_generator(self, index):
        average = [0 for _ in range(self.length//2+1)]
        k = 0
        yield
        coordinates = self.init_coordinates[index]
        prev_coordinates = self.prev_coordinates[index]
        while True:
            for _ in range(self.length/self.step):
                self.prev_coordinates.extend(coordinates[:self.step])
                del self.prev_coordinates[:self.step]
                del coordinates[:self.step]
                for j in range(self.step):
                    y = yield
                    coordinates.append(y)
                k += 1
                amplitude_spectrum = self.signalPipeline(coordinates, prev_coordinates)
                for i in range(len(amplitude_spectrum)):
                    average[i] = (average[i] * (k - 1) + amplitude_spectrum[i]) / k
                yield self.normaliseSpectrum(average)


class SingleAverage(FFT, Average, Single, PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self, "Single average FFT plot")
        FFT.__init__(self)
        Average.__init__(self)
        Single.__init__(self)

    def coordinates_generator(self, index):
        average = [0 for _ in range(self.length//2+1)]
        k = 0
        yield
        coordinates = [self.init_coordinates[i] for i in range(self.channel_count)]
        prev_coordinates = [self.prev_coordinates[i] for i in range(self.channel_count)]
        while True:
            for _ in range(self.length/self.step):
                for j in range(self.step):
                    for channel in range(self.channel_count):
                        y = yield
                        del coordinates[channel][0]
                        coordinates[channel].append(y)
                k += 1
                ffts = []
                for i in range(self.channel_count):
                    ffts.append(self.signalPipeline(coordinates[i], prev_coordinates[i]))
                for i in range(len(ffts[0])):
                    summ = 0
                    for j in range(self.channel_count):
                        summ += ffts[j][i]
                    average[i] = (average[i] * (k - 1) + summ/self.channel_count) / k
                yield self.normaliseSpectrum(average)


class SingleRegular(FFT, Regular, Single, PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self, "Single average FFT plot")
        FFT.__init__(self)
        Regular.__init__(self)
        Single.__init__(self)

    def coordinates_generator(self, index):
        average = [0 for _ in range(self.length//2+1)]
        yield
        coordinates = [self.init_coordinates[i] for i in range(self.channel_count)]
        prev_coordinates = [self.prev_coordinates[i] for i in range(self.channel_count)]
        while True:
            for _ in range(self.length/self.step):
                for j in range(self.step):
                    for channel in range(self.channel_count):
                        y = yield
                        del coordinates[channel][0]
                        coordinates[channel].append(y)
                ffts = []
                for i in range(self.channel_count):
                    ffts.append(self.signalPipeline(coordinates[i], prev_coordinates[i]))
                for i in range(len(ffts[0])):
                    summ = 0
                    for j in range(self.channel_count):
                        summ += ffts[j][i]
                    average[i] = summ/self.channel_count
                yield self.normaliseSpectrum(average)