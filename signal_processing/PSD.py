__author__ = 'Anti'

from signal_processing import Signal, SignalProcessing
import numpy as np
import constants as c


class AbstractPSD(Signal.AbstractSignal):
    def __init__(self):
        Signal.AbstractSignal.__init__(self)

    def normaliseSpectrum(self, fft):
        if self.options[c.OPTIONS_NORMALISE]:
            result = (fft/sum(fft))
            result[0] = None
            return result
        else:
            result = np.log10(fft)
            result[0] = None
            return result

    def signalPipeline(self, coordinates, window):
        windowed_signal = Signal.AbstractSignal.signalPipeline(self, coordinates, window)
        amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
        normalised_spectrum = self.normaliseSpectrum(amplitude_spectrum)
        return normalised_spectrum


class PSD(AbstractPSD):
    def __init__(self):
        AbstractPSD.__init__(self)

    def processSignal(self, signal, segment, i, k):
        signal.extend(segment)
        del signal[:len(segment)]
        return self.signalPipeline(signal, self.window_function)

    def processShortSignal(self, signal, i):
        return self.signalPipeline(signal, self.getWindowFunction(self.options, len(signal)))


class AveragePSD(AbstractPSD):
    def __init__(self):
        AbstractPSD.__init__(self)

    def processSignal(self, signal, segment, i, k):
        step = len(segment)
        for j in range(step):
            signal[i*step+j] = (signal[i*step+j] * (k - 1) + segment[j]) / k
        return self.signalPipeline(signal, self.window_function)

    def processShortSignal(self, signal, i):
        return self.signalPipeline(signal, self.getSegment(self.window_function, i))


class AbstractSumPSD(AbstractPSD):
    def __init__(self):
        AbstractPSD.__init__(self)
        self.generators = None
        # self.counter = 0

    def setup(self, options):
        self.channels = options[c.DATA_SENSORS]
        SignalProcessing.SignalProcessing.setup(self, options[c.DATA_OPTIONS])
        self.filter_prev_state = self.filterPrevState([0])
        self.generators = []
        for _ in range(len(self.channels)):
            new_generator = self.getGenerator()
            new_generator.setup(options)
            self.generators.append(new_generator)
        self.generator = self.coordinates_generator()
        self.generator.send(None)

    # def increaseCounter(self):
    #     if self.counter == self.options[c.OPTIONS_LENGTH]/self.options[c.OPTIONS_STEP]:
    #         self.counter = 0
    #     else:
    #         self.counter += 1
    #
    # def rollSignal(self, signal):
    #     if len(signal) == self.options[c.OPTIONS_LENGTH]:
    #         self.increaseCounter()
    #         return np.roll(signal, -self.counter*self.options[c.OPTIONS_STEP])
    #     else:
    #         return signal
    #
    # def signalPipeline(self, coordinates, window):
    #     windowed_signal = Signal.AbstractSignal.signalPipeline(self, coordinates, window)
    #     rolled_signal =
    #     amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
    #     normalised_spectrum = self.normaliseSpectrum(amplitude_spectrum)
    #     return normalised_spectrum

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


class SumAveragePSD(AbstractSumPSD):
    def __init__(self):
        AbstractSumPSD.__init__(self)

    def getGenerator(self):
        return Signal.RawAverageSignal()


class SumPsd(AbstractSumPSD):
    def __init__(self):
        AbstractSumPSD.__init__(self)

    def getGenerator(self):
        return Signal.RawSignal()