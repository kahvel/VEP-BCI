__author__ = 'Anti'
import PlotWindow
import FFT
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
        coordinates = []
        self.filter_prev_state = self.filterPrevState([0])
        for i in range(self.length/self.step):
            segment = []
            for j in range(self.step):
                y = yield
                segment.append(y)
            coordinates.extend(self.segmentPipeline(segment))
        spectrum = self.signalPipeline(coordinates)
        yield self.normaliseSpectrum(spectrum)
        while True:
            for i in range(self.length/self.step):
                segment = []
                for j in range(self.step):
                    y = yield
                    segment.append(y)
                coordinates.extend(self.segmentPipeline(segment))
                del coordinates[:self.step]
                spectrum = self.signalPipeline(coordinates)
                yield self.normaliseSpectrum(spectrum)


class MultipleAverage(FFTPlot, Average, Multiple, PlotWindow.MultiplePlotWindow):
    def __init__(self):
        PlotWindow.MultiplePlotWindow.__init__(self, "Average FFTs")
        FFTPlot.__init__(self)
        Average.__init__(self)
        Multiple.__init__(self)

    def coordinates_generator(self, index):
        k = 1
        coordinates = []
        self.filter_prev_state = self.filterPrevState([0])
        for _ in range(self.length/self.step):
            segment = []
            for j in range(self.step):
                y = yield
                segment.append(y)
            coordinates.extend(self.segmentPipeline(segment))
        average = self.signalPipeline(coordinates)
        yield self.normaliseSpectrum(average)
        while True:
            for _ in range(self.length/self.step):
                segment = []
                for j in range(self.step):
                    y = yield
                    segment.append(y)
                coordinates.extend(self.segmentPipeline(segment))
                del coordinates[:self.step]
                amplitude_spectrum = self.signalPipeline(coordinates)
                k += 1
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
        average = []
        k = 1
        coordinates = [[] for _ in range(self.channel_count)]
        self.filter_prev_state = [self.filterPrevState([0]) for _ in range(self.channel_count)]
        for _ in range(self.length/self.step):
            segment = [[] for _ in range(self.channel_count)]
            for j in range(self.step):
                for channel in range(self.channel_count):
                    y = yield
                    segment[channel].append(y)
            for i in range(self.channel_count):
                coordinates[i].extend(self.segmentPipeline(segment[i]))
        ffts = []
        for i in range(self.channel_count):
            ffts.append(self.signalPipeline(coordinates[i]))
        for i in range(len(ffts[0])):
            summ = 0
            for j in range(self.channel_count):
                summ += ffts[j][i]
            average.append(summ/self.channel_count)
        yield self.normaliseSpectrum(average)
        while True:
            for _ in range(self.length/self.step):
                segment = [[] for _ in range(self.channel_count)]
                for j in range(self.step):
                    for channel in range(self.channel_count):
                        y = yield
                        segment[channel].append(y)
                for i in range(self.channel_count):
                    coordinates[i].extend(self.segmentPipeline(segment[i]))
                    del coordinates[channel][:self.step]
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
        average = []
        coordinates = [[] for _ in range(self.channel_count)]
        self.filter_prev_state = self.filterPrevState([0])
        for _ in range(self.length/self.step):
            segment = [[] for _ in range(self.channel_count)]
            for j in range(self.step):
                for channel in range(self.channel_count):
                    y = yield
                    segment[channel].append(y)
            for i in range(self.channel_count):
                coordinates[i].extend(self.segmentPipeline(segment[i]))
        ffts = []
        for i in range(self.channel_count):
            ffts.append(self.signalPipeline(coordinates[i]))
        for i in range(len(ffts[0])):
            summ = 0
            for j in range(self.channel_count):
                summ += ffts[j][i]
            average.append(summ/self.channel_count)
        yield self.normaliseSpectrum(average)
        while True:
            for _ in range(self.length/self.step):
                segment = [[] for _ in range(self.channel_count)]
                for j in range(self.step):
                    for channel in range(self.channel_count):
                        y = yield
                        segment[channel].append(y)
                for i in range(self.channel_count):
                    coordinates[i].extend(self.segmentPipeline(segment[i]))
                    del coordinates[channel][:self.step]
                ffts = []
                for i in range(self.channel_count):
                    ffts.append(self.signalPipeline(coordinates[i]))
                for i in range(len(ffts[0])):
                    summ = 0
                    for j in range(self.channel_count):
                        summ += ffts[j][i]
                    average[i] = summ/self.channel_count
                yield self.normaliseSpectrum(average)