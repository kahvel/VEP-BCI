__author__ = 'Anti'

from signal_processing import SignalProcessing, Generator
import constants as c


class AbstractSignal(SignalProcessing.SignalPipeline):
    def __init__(self):
        SignalProcessing.SignalPipeline.__init__(self)


class AverageSignal(AbstractSignal):
    def __init__(self):
        AbstractSignal.__init__(self)

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


class Signal(AbstractSignal):
    def __init__(self):
        AbstractSignal.__init__(self)

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


class SumSignal(Signal):
    def __init__(self):
        AbstractSignal.__init__(self)

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


class SumAverageSignal(AverageSignal):
    def __init__(self):
        AverageSignal.__init__(self)

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
