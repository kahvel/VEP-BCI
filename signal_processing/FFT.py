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
        filtered_signal = []
        filter_prev_state = self.filterPrevState([0])
        for i in range(length/step):
            segment = []
            for j in range(step):
                y = yield
                segment.append(y)
            filtered_signal_segment, filter_prev_state = self.segmentPipeline(segment, filter_prev_state)
            filtered_signal.extend(filtered_signal_segment)
            spectrum = self.shortPipeline(filtered_signal)
            yield self.normaliseSpectrum(spectrum)
        while True:
            for i in range(length/step):
                segment = []
                for j in range(step):
                    y = yield
                    segment.append(y)
                filtered_signal_segment, filter_prev_state = self.segmentPipeline(segment, filter_prev_state)
                filtered_signal.extend(filtered_signal_segment)
                del filtered_signal[:step]
                spectrum = self.signalPipeline(filtered_signal)
                yield self.normaliseSpectrum(spectrum)


class NotSumAvg(FFT):
    def __init__(self):
        FFT.__init__(self)

    def coordinates_generator(self):
        step = self.options[c.OPTIONS_STEP]
        length = self.options[c.OPTIONS_LENGTH]
        k = 1
        filtered_signal = []
        filter_prev_state = self.filterPrevState([0])
        for _ in range(length/step):
            segment = []
            for j in range(step):
                y = yield
                segment.append(y)
            filtered_signal_segment, filter_prev_state = self.segmentPipeline(segment, filter_prev_state)
            filtered_signal.extend(filtered_signal_segment)
            average_spectrum = self.shortPipeline(filtered_signal)
            yield self.normaliseSpectrum(average_spectrum)
        while True:
            for _ in range(length/step):
                segment = []
                for j in range(step):
                    y = yield
                    segment.append(y)
                filtered_signal_segment, filter_prev_state = self.segmentPipeline(segment, filter_prev_state)
                filtered_signal.extend(filtered_signal_segment)
                del filtered_signal[:step]
                amplitude_spectrum = self.signalPipeline(filtered_signal)
                k += 1
                for i in range(len(amplitude_spectrum)):
                    average_spectrum[i] = (average_spectrum[i] * (k - 1) + amplitude_spectrum[i]) / k
                yield self.normaliseSpectrum(average_spectrum)


class SumAvg(FFT):
    def __init__(self):
        FFT.__init__(self)

    def coordinates_generator(self):
        step = self.options[c.OPTIONS_STEP]
        length = self.options[c.OPTIONS_LENGTH]
        channel_count = len(self.channels)
        # average_spectrum = []
        k = 1
        filtered_signal = [[] for _ in range(channel_count)]
        filter_prev_state = [self.filterPrevState([0]) for _ in range(channel_count)]
        for _ in range(length/step):
            segment = [[] for _ in range(channel_count)]
            for j in range(step):
                for channel in range(channel_count):
                    y = yield
                    segment[channel].append(y)
            for i in range(channel_count):
                filtered_signal_segment, filter_prev_state[i] = self.segmentPipeline(segment[i], filter_prev_state[i])
                filtered_signal[i].extend(filtered_signal_segment)
            ffts = []
            for i in range(channel_count):
                ffts.append(self.shortPipeline(filtered_signal[i]))
            average_spectrum = []
            for i in range(len(ffts[0])):
                summ = 0
                for j in range(channel_count):
                    summ += ffts[j][i]
                average_spectrum.append(summ/channel_count)
            yield self.normaliseSpectrum(average_spectrum)
        while True:
            for _ in range(length/step):
                segment = [[] for _ in range(channel_count)]
                for j in range(step):
                    for channel in range(channel_count):
                        y = yield
                        segment[channel].append(y)
                for i in range(channel_count):
                    filtered_signal_segment, filter_prev_state[i] = self.segmentPipeline(segment[i], filter_prev_state[i])
                    filtered_signal[i].extend(filtered_signal_segment)
                    del filtered_signal[i][:step]
                k += 1
                ffts = []
                for i in range(channel_count):
                    ffts.append(self.signalPipeline(filtered_signal[i]))
                for i in range(len(ffts[0])):
                    summ = 0
                    for j in range(channel_count):
                        summ += ffts[j][i]
                    average_spectrum[i] = (average_spectrum[i] * (k - 1) + summ/channel_count) / k
                yield self.normaliseSpectrum(average_spectrum)


class Sum(FFT):
    def __init__(self):
        FFT.__init__(self)

    def coordinates_generator(self):
        step = self.options[c.OPTIONS_STEP]
        length = self.options[c.OPTIONS_LENGTH]
        channel_count = len(self.channels)
        # average_spectrum = []
        filtered_signal = [[] for _ in range(channel_count)]
        filter_prev_state = [self.filterPrevState([0]) for _ in range(channel_count)]
        for _ in range(length/step):
            segment = [[] for _ in range(channel_count)]
            for j in range(step):
                for channel in range(channel_count):
                    y = yield
                    segment[channel].append(y)
            for i in range(channel_count):
                filtered_signal_segment, filter_prev_state[i] = self.segmentPipeline(segment[i], filter_prev_state[i])
                filtered_signal[i].extend(filtered_signal_segment)
            ffts = []
            for i in range(channel_count):
                ffts.append(self.shortPipeline(filtered_signal[i]))
            average_spectrum = []
            for i in range(len(ffts[0])):
                summ = 0
                for j in range(channel_count):
                    summ += ffts[j][i]
                average_spectrum.append(summ/channel_count)
            yield self.normaliseSpectrum(average_spectrum)
        while True:
            for _ in range(length/step):
                segment = [[] for _ in range(channel_count)]
                for j in range(step):
                    for channel in range(channel_count):
                        y = yield
                        segment[channel].append(y)
                for i in range(channel_count):
                    filtered_signal_segment, filter_prev_state[i] = self.segmentPipeline(segment[i], filter_prev_state[i])
                    filtered_signal[i].extend(filtered_signal_segment)
                    del filtered_signal[i][:step]
                ffts = []
                for i in range(channel_count):
                    ffts.append(self.signalPipeline(filtered_signal[i]))
                for i in range(len(ffts[0])):
                    summ = 0
                    for j in range(channel_count):
                        summ += ffts[j][i]
                    average_spectrum[i] = summ/channel_count
                yield self.normaliseSpectrum(average_spectrum)