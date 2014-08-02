__author__ = 'Anti'
import PlotWindow
import FFT
import copy
# import matplotlib.pyplot as plt


class FFTPlot(FFT.FFT):
    def __init__(self):
        FFT.FFT.__init__(self)

    def scale(self, coordinates, index, packet_count):
        result = []
        for i in range(len(coordinates)):
            result.append(i*self.window_width/len(coordinates))
            result.append(self.scaleY(coordinates[i], index, self.plot_count, 3.3, 0.2))
        return result

    def setInitSignal(self, min_packet, max_packet, averages, init_coordinates):
        for i in range(0, 512, 40):  # scale
            self.canvas.create_line(i, 0, i, 512, fill="red")
            self.canvas.create_text(i, 10, text=i/8)
        self.averages = averages
        self.init_coordinates = copy.deepcopy(init_coordinates)
        self.min_packet = []
        self.max_packet = []
        self.minp = min_packet
        self.maxp = max_packet
        import numpy as np
        for i in range(len(self.init_coordinates)):
            detrended_signal = self.detrendSignal(self.init_coordinates[i])
            filtered_signal = self.filterSignal(detrended_signal)
            windowed_signal = self.windowSignal(filtered_signal, self.window_function)
            spectrum = np.abs(np.fft.rfft(windowed_signal))
            spectrum = self.normaliseSpectrum(spectrum)
            self.canvas.delete(self.line)
            self.line = self.canvas.create_line(self.scalea(windowed_signal, 0, 0), fill="Red")
            self.min_packet.append(min(spectrum))
            self.max_packet.append(max(spectrum))


class Multiple(object):
    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[i].send(float(packet.sensors[self.sensor_names[i]]["value"]))


class Single(object):
    def sendPacket(self, packet):
        for i in range(self.channel_count):
            self.generators[0].send(float(packet.sensors[self.sensor_names[i]]["value"]))


class Regular(object):
    pass


class Average(object):
    pass


class MultipleRegular(FFTPlot, Regular, Multiple, PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self, "FFTs")
        self.line = self.canvas.create_line(0,0,0,0)
        FFTPlot.__init__(self)
        Regular.__init__(self)
        Multiple.__init__(self)

    def coordinates_generator(self, index):
        yield
        coordinates = []
        self.filter_prev_state = self.filterPrevState([0])
        for i in range(self.length/self.step):
            segment = []
            for j in range(self.step):
                y = yield
                segment.append(y)
            coordinates.extend(self.segmentPipeline(segment))
        spectrum = self.signalPipeline(coordinates)
        yield self.normaliseSpectrum(spectrum)[1:]
        while True:
            for i in range(self.length/self.step):
                segment = []
                for j in range(self.step):
                    y = yield
                    segment.append(y)

                del coordinates[:self.step]
                coordinates.extend(self.segmentPipeline(segment))
                spectrum = self.signalPipeline(coordinates)[1:]
                yield self.normaliseSpectrum(spectrum)


class MultipleAverage(FFTPlot, Average, Multiple, PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self, "Average FFTs")
        FFTPlot.__init__(self)
        Average.__init__(self)
        Multiple.__init__(self)

    def coordinates_generator(self, index):
        average = [0 for _ in range(self.length//2+1)]
        k = 0
        yield
        coordinates = self.init_coordinates[index]
        self.filter_prev_state = self.filterPrevState([0])
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


class SingleAverage(FFTPlot, Average, Single, PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self, "Sum of average FFTs")
        FFTPlot.__init__(self)
        Average.__init__(self)
        Single.__init__(self)

    def coordinates_generator(self, index):
        average = [0 for _ in range(self.length//2+1)]
        k = 0
        yield
        coordinates = [self.init_coordinates[i] for i in range(self.channel_count)]
        self.filter_prev_state = self.filterPrevState([0])
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


class SingleRegular(FFTPlot, Regular, Single, PlotWindow.SinglePlotWindow):
    def __init__(self):
        PlotWindow.SinglePlotWindow.__init__(self, "Sum of FFTs")
        FFTPlot.__init__(self)
        Regular.__init__(self)
        Single.__init__(self)

    def coordinates_generator(self, index):
        average = [0 for _ in range(self.length//2+1)]
        yield
        coordinates = [self.init_coordinates[i] for i in range(self.channel_count)]
        self.filter_prev_state = self.filterPrevState([0])
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