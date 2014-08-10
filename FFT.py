__author__ = 'Anti'
import numpy as np
import scipy.signal
import SignalProcessing


class FFT(SignalProcessing.SignalProcessing):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        SignalProcessing.SignalProcessing.__init__(self, options, window_function, channel_count, filter_coefficients)

    def normaliseSpectrum(self, fft):
        if self.options["Normalise"]:
            return (fft/sum(fft))[1:]
        else:
            return np.log10(fft)[1:]

    # def detrendSegment(self, signal):
    #     if self.options["Detrend"]:
    #         return scipy.signal.detrend(signal, bp=self.options["Breakpoints"])
    #     else:
    #         return signal

    # def scaleYa(self, y,  index, plot_count, new_max=-100, new_min=100):
    #     return ((((y - (-10)) * (new_max - new_min)) / (10 - (-10))) + new_min
    #             + index*self.window_height + self.window_height/2) / plot_count
    #
    # def scalea(self, coordinates, index, packet_count):
    #     result = []
    #     for i in range(len(coordinates)):
    #         result.append(i*self.window_width/len(coordinates))
    #         result.append(self.scaleYa(coordinates[i], index, self.plot_count))
    #     return result

    def segmentPipeline(self, coordinates, filter_prev_state):
        filtered_segment, filter_prev_state = self.filterSignal(coordinates, filter_prev_state)
        # detrended_segment = self.detrendSegment(filtered_segment)
        return filtered_segment, filter_prev_state

    def signalPipeline(self, coordinates):
        detrended_signal = self.detrendSignal(coordinates)
        windowed_signal = self.windowSignal(detrended_signal, self.window_function)
        amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
        # self.canvas.delete(self.line)
        # self.line = self.canvas.create_line(self.scalea(windowed_signal, 0, 0), fill="Red")
        return amplitude_spectrum


class MultipleRegular(FFT):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        FFT.__init__(self, options, window_function, channel_count, filter_coefficients)

    def coordinates_generator(self):
        step = self.options["Step"]
        length = self.options["Length"]
        # for i in range(0, 512, 40):  # scale
        #     self.canvas.create_line(i, 0, i, 512, fill="red")
        #     self.canvas.create_text(i, 10, text=i/8)
        coordinates = []
        filter_prev_state = self.filterPrevState([0])
        for i in range(length/step):
            segment = []
            for j in range(step):
                y = yield
                segment.append(y)
            result, filter_prev_state = self.segmentPipeline(segment, filter_prev_state)
            coordinates.extend(result)
        spectrum = self.signalPipeline(coordinates)
        yield self.normaliseSpectrum(spectrum)
        while True:
            for i in range(length/step):
                segment = []
                for j in range(step):
                    y = yield
                    segment.append(y)
                result, filter_prev_state = self.segmentPipeline(segment, filter_prev_state)
                coordinates.extend(result)
                del coordinates[:step]
                spectrum = self.signalPipeline(coordinates)
                yield self.normaliseSpectrum(spectrum)


class MultipleAverage(FFT):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        FFT.__init__(self, options, window_function, channel_count, filter_coefficients)

    def coordinates_generator(self):
        step = self.options["Step"]
        length = self.options["Length"]
        k = 1
        coordinates = []
        filter_prev_state = self.filterPrevState([0])
        for _ in range(length/step):
            segment = []
            for j in range(step):
                y = yield
                segment.append(y)
            result, filter_prev_state = self.segmentPipeline(segment, filter_prev_state)
            coordinates.extend(result)
        average = self.signalPipeline(coordinates)
        yield self.normaliseSpectrum(average)
        while True:
            for _ in range(length/step):
                segment = []
                for j in range(step):
                    y = yield
                    segment.append(y)
                result, filter_prev_state = self.segmentPipeline(segment, filter_prev_state)
                coordinates.extend(result)
                del coordinates[:step]
                amplitude_spectrum = self.signalPipeline(coordinates)
                k += 1
                for i in range(len(amplitude_spectrum)):
                    average[i] = (average[i] * (k - 1) + amplitude_spectrum[i]) / k
                yield self.normaliseSpectrum(average)


class SingleAverage(FFT):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        FFT.__init__(self, options, window_function, channel_count, filter_coefficients)

    def coordinates_generator(self):
        step = self.options["Step"]
        length = self.options["Length"]
        channel_count = self.channel_count
        average = []
        k = 1
        coordinates = [[] for _ in range(channel_count)]
        filter_prev_state = [self.filterPrevState([0]) for _ in range(channel_count)]
        for _ in range(length/step):
            segment = [[] for _ in range(channel_count)]
            for j in range(step):
                for channel in range(channel_count):
                    y = yield
                    segment[channel].append(y)
            for i in range(channel_count):
                result, filter_prev_state[i] = self.segmentPipeline(segment[i], filter_prev_state[i])
                coordinates[i].extend(result)
        ffts = []
        for i in range(channel_count):
            ffts.append(self.signalPipeline(coordinates[i]))
        for i in range(len(ffts[0])):
            summ = 0
            for j in range(channel_count):
                summ += ffts[j][i]
            average.append(summ/channel_count)
        yield self.normaliseSpectrum(average)
        while True:
            for _ in range(length/step):
                segment = [[] for _ in range(channel_count)]
                for j in range(step):
                    for channel in range(channel_count):
                        y = yield
                        segment[channel].append(y)
                for i in range(channel_count):
                    result, filter_prev_state[i] = self.segmentPipeline(segment[i], filter_prev_state[i])
                    coordinates[i].extend(result)
                    del coordinates[i][:step]
                k += 1
                ffts = []
                for i in range(channel_count):
                    ffts.append(self.signalPipeline(coordinates[i]))
                for i in range(len(ffts[0])):
                    summ = 0
                    for j in range(channel_count):
                        summ += ffts[j][i]
                    average[i] = (average[i] * (k - 1) + summ/channel_count) / k
                yield self.normaliseSpectrum(average)


class SingleRegular(FFT):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        FFT.__init__(self, options, window_function, channel_count, filter_coefficients)

    def coordinates_generator(self):
        step = self.options["Step"]
        length = self.options["Length"]
        channel_count = self.channel_count
        average = []
        coordinates = [[] for _ in range(channel_count)]
        filter_prev_state = [self.filterPrevState([0]) for _ in range(channel_count)]
        for _ in range(length/step):
            segment = [[] for _ in range(channel_count)]
            for j in range(step):
                for channel in range(channel_count):
                    y = yield
                    segment[channel].append(y)
            for i in range(channel_count):
                result, filter_prev_state[i] = self.segmentPipeline(segment[i], filter_prev_state[i])
                coordinates[i].extend(result)
        ffts = []
        for i in range(channel_count):
            ffts.append(self.signalPipeline(coordinates[i]))
        for i in range(len(ffts[0])):
            summ = 0
            for j in range(channel_count):
                summ += ffts[j][i]
            average.append(summ/channel_count)
        yield self.normaliseSpectrum(average)
        while True:
            for _ in range(length/step):
                segment = [[] for _ in range(channel_count)]
                for j in range(step):
                    for channel in range(channel_count):
                        y = yield
                        segment[channel].append(y)
                for i in range(channel_count):
                    result, filter_prev_state[i] = self.segmentPipeline(segment[i], filter_prev_state[i])
                    coordinates[i].extend(result)
                    del coordinates[i][:step]
                ffts = []
                for i in range(channel_count):
                    ffts.append(self.signalPipeline(coordinates[i]))
                for i in range(len(ffts[0])):
                    summ = 0
                    for j in range(channel_count):
                        summ += ffts[j][i]
                    average[i] = summ/channel_count
                yield self.normaliseSpectrum(average)


class Multiple(SignalProcessing.Multiple):
    def __init__(self):
        SignalProcessing.Multiple.__init__(self)

    def sendPacket(self, packet, generators, sensor_names):
        for i in range(len(sensor_names)):
            generators[i].send(float(packet.sensors[sensor_names[i]]["value"]))


class Single(SignalProcessing.Single):
    def __init__(self):
        SignalProcessing.Single.__init__(self)

    def sendPacket(self, packet, generators, sensor_names):
        for i in range(len(sensor_names)):
            generators[0].send(float(packet.sensors[sensor_names[i]]["value"]))