__author__ = 'Anti'

from signal_processing import SignalProcessing
import numpy as np
import constants as c


class FFT(SignalProcessing.SignalProcessing):
    def __init__(self):
        SignalProcessing.SignalProcessing.__init__(self)

    def normaliseSpectrum(self, fft):
        if self.options[c.OPTIONS_NORMALISE]:
            result = (fft/sum(fft))
            # result[0] = 0
            return result
        else:
            result = np.log10(fft)
            # result[0] = 0
            return result

    # def detrendSegment(self, signal):
    #     if self.options["Detrend"]:
    #         return scipy.signal.detrend(signal, bp=self.options["Breakpoints"])
    #     else:
    #         return signal

    def shortPipeline(self, coordinates):
        detrended_signal = self.detrendSignal(coordinates)
        window_function = self.getWindowFunction(self.options, len(detrended_signal))
        windowed_signal = self.windowSignal(detrended_signal, window_function)
        amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
        return amplitude_spectrum

    def segmentPipeline(self, coordinates, filter_prev_state):
        filtered_segment, filter_prev_state = self.filterSignal(coordinates, filter_prev_state)
        # detrended_segment = self.detrendSegment(filtered_segment)
        return filtered_segment, filter_prev_state

    def signalPipeline(self, coordinates):
        detrended_signal = self.detrendSignal(coordinates)
        windowed_signal = self.windowSignal(detrended_signal, self.window_function)
        amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
        return amplitude_spectrum


class NotSum(FFT):
    def __init__(self):
        FFT.__init__(self)

    def coordinates_generator(self):
        step = self.options[c.OPTIONS_STEP]
        length = self.options[c.OPTIONS_LENGTH]
        coordinates = []
        filter_prev_state = self.filterPrevState([0])
        for i in range(length/step):
            segment = []
            for j in range(step):
                y = yield
                segment.append(y)
            result, filter_prev_state = self.segmentPipeline(segment, filter_prev_state)
            coordinates.extend(result)
            spectrum = self.shortPipeline(coordinates)
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


class NotSumAvg(FFT):
    def __init__(self):
        FFT.__init__(self)

    def coordinates_generator(self):
        step = self.options[c.OPTIONS_STEP]
        length = self.options[c.OPTIONS_LENGTH]
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
            average = self.shortPipeline(coordinates)
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


class SumAvg(FFT):
    def __init__(self):
        FFT.__init__(self)

    def coordinates_generator(self):
        step = self.options[c.OPTIONS_STEP]
        length = self.options[c.OPTIONS_LENGTH]
        channel_count = len(self.channels)
        # average = []
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
                ffts.append(self.shortPipeline(coordinates[i]))
            average = []
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


class Sum(FFT):
    def __init__(self):
        FFT.__init__(self)

    def coordinates_generator(self):
        step = self.options[c.OPTIONS_STEP]
        length = self.options[c.OPTIONS_LENGTH]
        channel_count = len(self.channels)
        # average = []
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
                ffts.append(self.shortPipeline(coordinates[i]))
            average = []
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