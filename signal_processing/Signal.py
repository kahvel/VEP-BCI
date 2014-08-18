__author__ = 'Anti'

from signal_processing import SignalProcessing
import numpy as np


class Signal(SignalProcessing.SignalProcessing):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        SignalProcessing.SignalProcessing.__init__(self, options, window_function, channel_count, filter_coefficients)

    def getSegment(self, array, i):
        if array is not None:
            step = self.options["Step"]
            return array[i*step:i*step+step]
        else:
            return None

    def signalPipeline(self, signal, i, filter_prev_state):
        detrended_signal = self.detrendSignal(signal)
        filtered_signal, filter_prev_state = self.filterSignal(detrended_signal, filter_prev_state)
        window_segment = self.getSegment(self.window_function, i)
        windowed_signal = self.windowSignal(filtered_signal, window_segment)
        return windowed_signal, filter_prev_state


class MultipleAverage(Signal):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        Signal.__init__(self, options, window_function, channel_count, filter_coefficients)

    def coordinates_generator(self):
        step = self.options["Step"]
        length = self.options["Length"]
        result = [0 for _ in range(length)]
        coordinates = [0 for _ in range(step)]
        k = 0
        filter_prev_state = self.filterPrevState([0])
        while True:
            k += 1
            for i in range(length/step):
                for j in range(step):
                    y = yield
                    coordinates[j] = y
                processed_signal, filter_prev_state = self.signalPipeline(coordinates, i, filter_prev_state)
                for j in range(step):
                    result[i*step+j] = (result[i*step+j] * (k - 1) + processed_signal[j]) / k
                yield result


class MultipleRegular(Signal):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        Signal.__init__(self, options, window_function, channel_count, filter_coefficients)

    def coordinates_generator(self):
        step = self.options["Step"]
        length = self.options["Length"]
        coordinates = [0 for _ in range(step)]
        result = [0 for _ in range(length)]
        filter_prev_state = self.filterPrevState([0])
        while True:
            for i in range(length/step):
                for j in range(step):
                    y = yield
                    coordinates[j] = y
                processed_signal, filter_prev_state = self.signalPipeline(coordinates, i, filter_prev_state)
                for j in range(step):
                    result[i*step+j] = processed_signal[j]
                yield result


class SingleAverage(Signal):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        Signal.__init__(self, options, window_function, channel_count, filter_coefficients)

    def coordinates_generator(self):
        step = self.options["Step"]
        length = self.options["Length"]
        channel_count = self.channel_count
        result = [0 for _ in range(length)]
        coordinates = [[0 for _ in range(length)] for _ in range(channel_count)]
        segment = [[0 for _ in range(step)] for _ in range(channel_count)]
        filter_prev_state = [self.filterPrevState([0]) for _ in range(channel_count)]
        k = 0
        while True:
            k += 1
            for i in range(length/step):
                for j in range(step):
                    for channel in range(channel_count):
                        y = yield
                        segment[channel][j] = y
                for channel in range(channel_count):
                    processed_signal, filter_prev_state[channel] = self.signalPipeline(segment[channel], i, filter_prev_state[channel])
                    for j in range(step):
                        coordinates[channel][j] = processed_signal[j]
                for j in range(step):
                    summ = 0
                    for channel in range(channel_count):
                        summ += coordinates[channel][j]
                    result[i*step+j] = (result[i*step+j] * (k - 1) + summ/channel_count) / k
                yield result


class SingleRegular(Signal):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        Signal.__init__(self, options, window_function, channel_count, filter_coefficients)

    def coordinates_generator(self):
        step = self.options["Step"]
        length = self.options["Length"]
        channel_count = self.channel_count
        result = [0 for _ in range(length)]
        coordinates = [[0 for _ in range(length)] for _ in range(channel_count)]
        segment = [[0 for _ in range(step)] for _ in range(channel_count)]
        filter_prev_state = [self.filterPrevState([0]) for _ in range(channel_count)]
        k = 0
        while True:
            k += 1
            for i in range(length/step):
                for j in range(step):
                    for channel in range(channel_count):
                        y = yield
                        segment[channel][j] = y
                for channel in range(channel_count):
                    processed_signal, filter_prev_state[channel] = self.signalPipeline(segment[channel], i, filter_prev_state[channel])
                    for j in range(step):
                        coordinates[channel][j] = processed_signal[j]
                for j in range(step):
                    summ = 0
                    for channel in range(channel_count):
                        summ += coordinates[channel][j]
                    result[i*step+j] = summ/channel_count
                yield result