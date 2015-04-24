__author__ = 'Anti'

from signal_processing import Signal, SignalProcessing, Generator
import numpy as np
import constants as c


class AbstractPSD(SignalProcessing.SignalPipeline):
    def __init__(self):
        SignalProcessing.SignalPipeline.__init__(self)

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
        windowed_signal = SignalProcessing.SignalPipeline.signalPipeline(self, coordinates, window)
        amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
        normalised_spectrum = self.normaliseSpectrum(amplitude_spectrum)
        return normalised_spectrum


class PSD(AbstractPSD):
    def __init__(self):
        AbstractPSD.__init__(self)

    def getGenerator(self, options):
        return Generator.Generator(
            self.processSignal,
            self.processShortSignal,
            self.signalPipeline
        )

    def processSignal(self, signal, segment, i, k, pipelineFunction):
        signal.extend(segment)
        del signal[:len(segment)]
        return pipelineFunction(signal, self.window_function)

    def processShortSignal(self, signal, i, pipelineFunction):
        return pipelineFunction(signal, self.getWindowFunction(self.options, len(signal)))


class AveragePSD(AbstractPSD):
    def __init__(self):
        AbstractPSD.__init__(self)

    def getGenerator(self, options):
        return Generator.Generator(
            self.processSignal,
            self.processShortSignal,
            self.signalPipeline
        )

    def processSignal(self, signal, segment, i, k, pipelineFunction):
        step = len(segment)
        for j in range(step):
            signal[i*step+j] = (signal[i*step+j] * (k - 1) + segment[j]) / k
        return pipelineFunction(signal, self.window_function)

    def processShortSignal(self, signal, i, pipelineFunction):
        return pipelineFunction(signal, self.getSegment(self.window_function, i))


class SumAveragePSD(AveragePSD):
    def __init__(self):
        AveragePSD.__init__(self)

    def getGenerator(self, options):
        return Generator.SumGenerator(
            self.processSignal,
            self.processShortSignal,
            self.innerPipeline,
            self.signalPipeline,
            self.processSumSignals
        )

    def innerPipeline(self, signal, window):
        return signal

    def processSumSignals(self, signal, pipelineFunction):
        return pipelineFunction(signal, self.window_function)


class SumPsd(PSD):
    def __init__(self):
        PSD.__init__(self)

    def getGenerator(self, options):
        return Generator.SumGenerator(
            self.processSignal,
            self.processShortSignal,
            self.innerPipeline,
            self.signalPipeline,
            self.processSumSignals
        )

    def innerPipeline(self, signal, window):
        return signal

    def processSumSignals(self, signal, pipelineFunction):
        return pipelineFunction(signal, self.window_function)
