__author__ = 'Anti'

from signal_processing import SignalProcessing
import constants as c
import numpy as np


class AbstractSignal(SignalProcessing.SignalProcessing):
    def __init__(self):
        SignalProcessing.SignalProcessing.__init__(self)
        self.filter_prev_state = None
        self.generator = None
        self.channels = None

    def getSegment(self, array, i):
        if array is not None:
            step = self.options[c.OPTIONS_STEP]
            return array[i*step:i*step+step]
        else:
            return None

    def signalPipeline(self, coordinates, window):
        detrended_signal = self.detrendSignal(coordinates)
        filtered_signal, self.filter_prev_state = self.filterSignal(detrended_signal, self.filter_prev_state)
        windowed_signal = self.windowSignal(filtered_signal, window)
        return windowed_signal

    def coordinates_generator(self, step, length):
        raise NotImplementedError("coordinates_generator not implemented!")

    def setup(self, options):
        self.channels = options[c.DATA_SENSORS]  # TODO give this as argument??
        options = options[c.DATA_OPTIONS]
        SignalProcessing.SignalProcessing.setup(self, options)
        self.filter_prev_state = self.filterPrevState([0])

    def send(self, message):
        return self.generator.send(message)

    def next(self):
        self.generator.next()


class AverageSignal(AbstractSignal):
    def __init__(self):
        AbstractSignal.__init__(self)

    def setup(self, options):
        AbstractSignal.setup(self, options)
        self.generator = self.coordinates_generator(options[c.DATA_OPTIONS][c.OPTIONS_STEP], options[c.DATA_OPTIONS][c.OPTIONS_LENGTH])
        self.generator.send(None)

    def coordinates_generator(self, step, length):
        average_signal = []
        for i in range(length/step):
            segment = []
            for j in range(step):
                y = yield
                segment.append(y)
            average_signal.extend(segment)
            processed_average_signal = self.signalPipeline(average_signal, self.getSegment(self.window_function, i))
            yield processed_average_signal
        k = 1
        while True:
            k += 1
            for i in range(length/step):
                segment = []
                for j in range(step):
                    y = yield
                    segment.append(float(y))
                for j in range(step):
                    average_signal[i*step+j] = (average_signal[i*step+j] * (k - 1) + segment[j]) / k
                processed_average_signal = self.signalPipeline(average_signal, self.window_function)
                yield processed_average_signal


class Signal(AbstractSignal):
    def __init__(self):
        AbstractSignal.__init__(self)

    def setup(self, options):
        AbstractSignal.setup(self, options)
        self.generator = self.coordinates_generator(options[c.DATA_OPTIONS][c.OPTIONS_STEP], options[c.DATA_OPTIONS][c.OPTIONS_LENGTH])
        self.generator.send(None)

    def coordinates_generator(self, step, length):
        signal = []
        for i in range(length/step):
            segment = []
            for j in range(step):
                y = yield
                segment.append(y)
            signal.extend(segment)
            result = self.signalPipeline(signal, self.getWindowFunction(self.options, len(signal)))
            yield result
        while True:
            for i in range(length/step):
                segment = []
                for j in range(step):
                    y = yield
                    segment.append(y)
                signal.extend(segment)
                del signal[:step]
                result = self.signalPipeline(signal, self.window_function)
                yield result


class AbstractSumSignal(AbstractSignal):
    def __init__(self):
        AbstractSignal.__init__(self)
        self.generators = None

    def setup(self, options):
        AbstractSignal.setup(self, options)
        channel_count = len(self.channels)
        self.generators = []
        for _ in range(channel_count):
            new_generator = self.getGenerator()
            new_generator.setup(options)
            self.generators.append(new_generator)
        self.generator = self.coordinates_generator()
        self.generator.send(None)

    def getGenerator(self):
        raise NotImplementedError("getGenerator not implemented!")

    def coordinates_generator(self, step=None, length=None):
        while True:
            signals = []
            for generator in self.generators:
                y = yield
                signals.append(generator.send(y))
            if None not in signals:
                sum_of_signals = np.mean(signals, axis=0)
                result = self.signalPipeline(sum_of_signals, self.window_function)
                yield result
                for generator in self.generators:
                    generator.next()


class RawSignal(Signal):
    def __init__(self):
        Signal.__init__(self)

    def signalPipeline(self, coordinates, window):
        return coordinates


class RawAverageSignal(AverageSignal):
    def __init__(self):
        AverageSignal.__init__(self)

    def signalPipeline(self, coordinates, window):
        return coordinates


class SumSignal(AbstractSumSignal):
    def __init__(self):
        AbstractSumSignal.__init__(self)

    def getGenerator(self):
        return RawSignal()


class SumAverageSignal(AbstractSumSignal):
    def __init__(self):
        AbstractSumSignal.__init__(self)

    def getGenerator(self):
        return RawAverageSignal()
