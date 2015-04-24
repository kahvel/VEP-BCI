__author__ = 'Anti'

from signal_processing import SignalProcessing
import numpy as np


class AbstractPSD(object):
    def signalPipeline(self, signal, window):
        detrended_signal = self.detrendSignal(signal)
        filtered_signal, self.filter_prev_state = self.filterSignal(detrended_signal, self.filter_prev_state)
        windowed_signal = self.windowSignal(filtered_signal, window)
        amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
        normalised_spectrum = self.normaliseSpectrum(amplitude_spectrum)
        return normalised_spectrum


class PSD(AbstractPSD, SignalProcessing.Signal):
    def __init__(self):
        AbstractPSD.__init__(self)
        SignalProcessing.Signal.__init__(self, self.signalPipeline)


class AveragePSD(AbstractPSD, SignalProcessing.AverageSignal):
    def __init__(self):
        AbstractPSD.__init__(self)
        SignalProcessing.AverageSignal.__init__(self, self.signalPipeline)


class SumAveragePSD(AveragePSD, SignalProcessing.SumAverageSignal):
    def __init__(self):
        AveragePSD.__init__(self)
        SignalProcessing.SumAverageSignal.__init__(self, self.signalPipeline)


class SumPsd(PSD, SignalProcessing.SumSignal):
    def __init__(self):
        PSD.__init__(self)
        SignalProcessing.SumSignal.__init__(self, self.signalPipeline)
