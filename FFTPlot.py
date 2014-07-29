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
            return np.log10(fft/sum(fft))
        else:
            return np.log10(fft)

    def filterPrevState(self, filtered_signal):  # We calculate prev filter state from signal[:self.step], because
                                                 # we save other values for next FFT (and also for next filtering)
        if self.filter:
            return scipy.signal.lfiltic(1.0, self.filter_coefficients, filtered_signal[:self.step])
        else:
            return None

    def setInitSignal(self, min_packet, max_packet, averages, initial_packets):
        self.averages = averages
        self.initial_packets = initial_packets
        self.min_packet = []
        self.max_packet = []
        for packets in initial_packets:
            spectrum = self.normaliseSpectrum(self.signalPipeline(packets))[1:]
            self.min_packet.append(min(spectrum))
            self.max_packet.append(max(spectrum))

    def signalPipeline(self, coordinates):
        detrended_signal = scipy.signal.detrend(coordinates)
        filtered_signal = self.filterSignal(detrended_signal)
        self.prev_filter = self.filterPrevState(filtered_signal)
        windowed_signal = self.windowSignal(filtered_signal, self.window_function)
        amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
        # normalised_spectrum = self.normaliseSpectrum(amplitude_spectrum)
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
        FFT.__init__(self)
        Regular.__init__(self)
        Multiple.__init__(self)

    # def scaleasd(self, coordinates, index):
    #     result = []
    #     for i in range(len(coordinates)):
    #         result.append(i)
    #         result.append(self.scaleY(coordinates[i],  index, self.plot_count))
    #     return result
    #
    # def scaleY(self, y,  index, plot_count):
    #     # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    #     return ((((y - self.min[index]) * (-100 - 100)) / (self.max[index] - self.min[index])) + 100
    #             + index*self.window_height + self.window_height/2) / plot_count

    def coordinates_generator(self, index):
        yield
        coordinates = self.initial_packets[index][:]
        self.prev_filter = self.filterInitState(index)
        while True:
            for i in range(self.length/self.step):
                del coordinates[:self.step]
                for j in range(self.step):
                    y = yield
                    coordinates.append(y)
                spectrum = self.signalPipeline(coordinates)
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
        coordinates = self.initial_packets[index][:]
        self.prev_filter = self.filterInitState(index)
        while True:
            for _ in range(self.length/self.step):
                del coordinates[:self.step]
                for j in range(self.step):
                    y = yield
                    coordinates.append(y)
                k += 1
                amplitude_spectrum = self.signalPipeline(coordinates)
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
        coordinates = [self.initial_packets[i][:] for i in range(self.channel_count)]
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
                    ffts.append(self.signalPipeline(coordinates[i]))
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
        coordinates = [self.initial_packets[i][:] for i in range(self.channel_count)]
        while True:
            for _ in range(self.length/self.step):
                for j in range(self.step):
                    for channel in range(self.channel_count):
                        y = yield
                        del coordinates[channel][0]
                        coordinates[channel].append(y)
                ffts = []
                for i in range(self.channel_count):
                    ffts.append(self.signalPipeline(coordinates[i]))
                for i in range(len(ffts[0])):
                    summ = 0
                    for j in range(self.channel_count):
                        summ += ffts[j][i]
                    average[i] = summ/self.channel_count
                yield self.normaliseSpectrum(average)