__author__ = 'Anti'

from signal_processing import SignalProcessing, Generator
import constants as c


class AbstractSignal(SignalProcessing.SignalProcessing):
    def __init__(self):
        SignalProcessing.SignalProcessing.__init__(self)

    def getSegment(self, array, i):
        if array is not None:
            step = self.options[c.OPTIONS_STEP]
            return array[i*step:i*step+step]
        else:
            return None

    def signalPipeline(self, signal, window):
        detrended_signal = self.detrendSignal(signal)
        filtered_signal, self.filter_prev_state = self.filterSignal(detrended_signal, self.filter_prev_state)
        windowed_signal = self.windowSignal(filtered_signal, window)
        return windowed_signal

    def innerPipeline(self, signal, window):
        raise NotImplementedError("innerPipeline not implemented!")

    def processSumSignals(self, signal, pipelineFunction):
        raise NotImplementedError("processSumSignals not implemented!")

    def processSignal(self, signal, segment, i, k, pipelineFunction):
        raise NotImplementedError("processSignal not implemented!")

    def processShortSignal(self, signal, i, pipelineFunction):
        raise NotImplementedError("processShortSignal not implemented!")


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
