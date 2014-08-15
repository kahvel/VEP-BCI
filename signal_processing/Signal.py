__author__ = 'Anti'

from signal_processing import SignalProcessing
import numpy as np
import Queue


class Signal(SignalProcessing.SignalProcessing):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        SignalProcessing.SignalProcessing.__init__(self, options, window_function, channel_count, filter_coefficients)

    def getSegment(self, array, i):
        if array is not None:
            step = self.options["Step"]
            return array[i*step:i*step+step]
        else:
            return None

    def addPrevious(self, signal, previous):
        if isinstance(signal, list):
            return [previous] + signal
        else:
            return np.insert(signal, 0, previous)

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
        average = [0 for _ in range(length)]
        k = 0
        prev_coordinate = 0
        filter_prev_state = self.filterPrevState([0])
        while True:
            k += 1
            for i in range(length/step):
                for j in range(step):
                    y = yield
                    average[i*step+j] = (average[i*step+j] * (k - 1) + y) / k
                signal_segment = self.getSegment(average, i)
                result, filter_prev_state = self.signalPipeline(signal_segment, i, filter_prev_state)
                yield Queue.deque(self.addPrevious(result, prev_coordinate))
                prev_coordinate = result[-1]


class MultipleRegular(Signal):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        Signal.__init__(self, options, window_function, channel_count, filter_coefficients)

    def coordinates_generator(self):
        step = self.options["Step"]
        length = self.options["Length"]
        average = [0 for _ in range(step)]
        prev_coordinate = 0
        filter_prev_state = self.filterPrevState([0])
        while True:
            for i in range(length/step):
                for j in range(step):
                    y = yield
                    average[j] = y
                result, filter_prev_state = self.signalPipeline(average, i, filter_prev_state)
                yield Queue.deque(self.addPrevious(result, prev_coordinate))
                prev_coordinate = result[-1]


class SingleAverage(Signal):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        Signal.__init__(self, options, window_function, channel_count, filter_coefficients)

    def coordinates_generator(self):
        step = self.options["Step"]
        length = self.options["Length"]
        channel_count = self.channel_count
        average = [0 for _ in range(length)]
        prev_coordinate = 0
        filter_prev_state = [self.filterPrevState([0]) for _ in range(channel_count)]
        k = 0
        while True:
            k += 1
            for i in range(length/step):
                coordinates = [[] for _ in range(channel_count)]
                segment = [[] for _ in range(channel_count)]
                for j in range(step):
                    for channel in range(channel_count):
                        y = yield
                        segment[channel].append(y)
                for j in range(channel_count):
                    result, filter_prev_state[j] = self.signalPipeline(segment[j], i, filter_prev_state[j])
                    coordinates[j].extend(result)
                for j in range(len(coordinates[0])):
                    summ = 0
                    for channel in range(channel_count):
                        summ += coordinates[channel][j]
                    average[i*step+j] = (average[i*step+j] * (k - 1) + summ/channel_count) / k
                asd = self.getSegment(average, i)
                yield Queue.deque(self.addPrevious(asd, prev_coordinate))
                prev_coordinate = asd[-1]


class SingleRegular(Signal):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        Signal.__init__(self, options, window_function, channel_count, filter_coefficients)

    def coordinates_generator(self):
        step = self.options["Step"]
        length = self.options["Length"]
        channel_count = self.channel_count
        average = [0 for _ in range(step)]
        prev_coordinate = 0
        filter_prev_state = [self.filterPrevState([0]) for _ in range(channel_count)]
        while True:
            for i in range(length/step):
                coordinates = [[] for _ in range(channel_count)]
                segment = [[] for _ in range(channel_count)]
                for j in range(step):
                    for channel in range(channel_count):
                        y = yield
                        segment[channel].append(y)
                for j in range(channel_count):
                    result, filter_prev_state[j] = self.signalPipeline(segment[j], i, filter_prev_state[j])
                    coordinates[j].extend(result)
                for j in range(len(coordinates[0])):
                    summ = 0
                    for k in range(channel_count):
                        summ += coordinates[k][j]
                    average[j] = summ/channel_count
                yield Queue.deque(self.addPrevious(average, prev_coordinate))
                prev_coordinate = average[-1]