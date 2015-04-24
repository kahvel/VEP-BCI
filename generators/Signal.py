__author__ = 'Anti'

from generators import SignalProcessing


class AbstractSignal(object):
    def signalPipeline(self, signal, window):
        detrended_signal = self.detrendSignal(signal)
        filtered_signal, self.filter_prev_state = self.filterSignal(detrended_signal, self.filter_prev_state)
        windowed_signal = self.windowSignal(filtered_signal, window)
        return windowed_signal


class AverageSignal(AbstractSignal, SignalProcessing.AverageSignal):
    def __init__(self):
        AbstractSignal.__init__(self)
        SignalProcessing.AverageSignal.__init__(self, self.signalPipeline)


class Signal(AbstractSignal, SignalProcessing.Signal):
    def __init__(self):
        AbstractSignal.__init__(self)
        SignalProcessing.Signal.__init__(self, self.signalPipeline)


class SumSignal(Signal, SignalProcessing.SumSignal):
    def __init__(self):
        AbstractSignal.__init__(self)
        SignalProcessing.SumSignal.__init__(self, self.signalPipeline)


class SumAverageSignal(AverageSignal, SignalProcessing.SumAverageSignal):
    def __init__(self):
        AverageSignal.__init__(self)
        SignalProcessing.SumAverageSignal.__init__(self, self.signalPipeline)
