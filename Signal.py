__author__ = 'Anti'
import SignalProcessing
import numpy as np
import Queue


class Signal(SignalProcessing.SignalProcessing):
    def __init__(self):
        SignalProcessing.SignalProcessing.__init__(self)

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

    def signalPipeline(self, signal, i, prev_coordinate, filter_prev_state):
        detrended_signal = self.detrendSignal(signal)
        filtered_signal, filter_prev_state = self.filterSignal(detrended_signal, filter_prev_state)
        window_segment = self.getSegment(self.window_function, i)
        windowed_signal = self.windowSignal(filtered_signal, window_segment)
        extended_signal = self.addPrevious(windowed_signal, prev_coordinate)
        return extended_signal, filter_prev_state


class Average(Signal):
    def __init__(self):
        Signal.__init__(self)

    def coordinates_generator(self, index):
        step = self.options["Step"]
        length = self.options["Length"]
        average = [0 for _ in range(length)]
        k = 0
        prev_coordinate = 0
        yield
        filter_prev_state = self.filterPrevState([0])
        while True:
            k += 1
            for i in range(length/step):
                for j in range(step):
                    y = yield
                    average[i*step+j] = (average[i*step+j] * (k - 1) + y) / k
                signal_segment = self.getSegment(average, i)
                result, filter_prev_state = self.signalPipeline(signal_segment, i, prev_coordinate, filter_prev_state)
                yield Queue.deque(result)
                prev_coordinate = result[-1]


class Regular(Signal):
    def __init__(self):
        Signal.__init__(self)

    def coordinates_generator(self, index):
        step = self.options["Step"]
        length = self.options["Length"]
        average = [0 for _ in range(step)]
        prev_coordinate = 0
        yield
        filter_prev_state = self.filterPrevState([0])
        while True:
            for i in range(length/step):
                for j in range(step):
                    y = yield
                    average[j] = y
                result, filter_prev_state = self.signalPipeline(average, i, prev_coordinate, filter_prev_state)
                yield Queue.deque(result)
                prev_coordinate = result[-1]