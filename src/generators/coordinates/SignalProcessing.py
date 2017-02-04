import scipy.signal
import numpy as np

import constants as c
from generators import AbstractGenerator

try:
    from rpy2.robjects.packages import importr
except ImportError:
    print "rpy2 library not found. Breakpoint detrend cannot be used."


class SignalProcessing(AbstractGenerator.AbstractMyGenerator):
    def __init__(self):
        AbstractGenerator.AbstractMyGenerator.__init__(self)
        self.options = None
        self.channels = None
        self.window_function = None
        self.filter_coefficients = None
        self.breakpoints = None
        self.filter_prev_state = None
        self.base_r_library = None
        self.changepoint_r_library = None

    def setup(self, options):
        AbstractGenerator.AbstractMyGenerator.setup(self, options)
        self.options = options[c.DATA_OPTIONS]
        self.filter_coefficients = self.getFilter(self.options)
        self.breakpoints = self.getBreakpoints(self.options)
        self.filter_prev_state = self.getFilterPrevState([0])
        self.changepoint_r_library = importr("changepoint")
        self.base_r_library = importr("base")

    def getFilter(self, options):
        if options[c.OPTIONS_FILTER] == c.NONE_FILTER:
            return None
        nyq = c.HEADSET_FREQ/2.0
        to_value = options[c.OPTIONS_TO]
        from_value = options[c.OPTIONS_FROM]
        num_taps = options[c.OPTIONS_TAPS]
        if options[c.OPTIONS_FILTER] == c.LOWPASS_FILTER:
            return scipy.signal.firwin(num_taps, to_value/nyq)
        elif options[c.OPTIONS_FILTER] == c.HIGHPASS_FILTER:
            return scipy.signal.firwin(num_taps, from_value/nyq, pass_zero=False)
        elif options[c.OPTIONS_FILTER] == c.BANDPASS_FILTER:
            return scipy.signal.firwin(num_taps, [from_value/nyq, to_value/nyq], pass_zero=False)
        else:
            raise ValueError("Illegal filter value in getFilter: " + options[c.OPTIONS_FILTER])

    def getBreakpoints(self, options):
        if options[c.OPTIONS_DETREND] in (c.LINEAR_DETREND, c.CONSTANT_DETREND):
            breakpoints_count = options[c.OPTIONS_BREAK]+1
            breakpoints_list = []
            for i in range(breakpoints_count):
                breakpoints_list.append(options[c.OPTIONS_LENGTH]/breakpoints_count*i)
            return breakpoints_list
        elif options[c.OPTIONS_DETREND] == c.NONE_DETREND:
            return 0
        elif options[c.OPTIONS_DETREND] == c.BREAKPOINT_DETREND:
            pass
        else:
            raise ValueError("Illegal detrend value in getBreakpoints: " + options[c.OPTIONS_DETREND])

    def filterSignal(self, signal, filter_prev_state):
        if self.options[c.OPTIONS_FILTER] == c.NONE_FILTER:
            return signal, None
        elif self.options[c.OPTIONS_FILTER] in c.FILTER_NAMES:
            return scipy.signal.lfilter(self.filter_coefficients, 1.0, signal, zi=filter_prev_state)
        else:
            raise ValueError("Illegal filter value in filterSignal: " + self.options[c.OPTIONS_FILTER])

    def getShortBreakpoints(self, signal):
        return [breakpoint for breakpoint in self.breakpoints if breakpoint < len(signal)]

    def detrendSignal(self, signal):
        if self.options[c.OPTIONS_DETREND] == c.LINEAR_DETREND:
            return scipy.signal.detrend(signal, type="linear", bp=self.getShortBreakpoints(signal))
        elif self.options[c.OPTIONS_DETREND] == c.CONSTANT_DETREND:
            return scipy.signal.detrend(signal, type="constant", bp=self.getShortBreakpoints(signal))
        elif self.options[c.OPTIONS_DETREND] == c.NONE_DETREND:
            return signal
        elif self.options[c.OPTIONS_DETREND] == c.BREAKPOINT_DETREND:
            cpts = self.changepoint_r_library.cpt_meanvar(self.base_r_library.unlist(list(signal)), method="PELT")
            break_points = self.changepoint_r_library.cpts(cpts)
            return scipy.signal.detrend(signal, type="linear", bp=break_points)
        else:
            raise ValueError("Illegal detrend value in detrendSignal: " + self.options[c.OPTIONS_DETREND])

    def windowSignal(self, signal, window):
        if self.options[c.OPTIONS_WINDOW] == c.WINDOW_NONE:
            return signal
        elif self.options[c.OPTIONS_WINDOW] in c.WINDOW_FUNCTION_NAMES:
            return signal*window
        else:
            raise ValueError("Illegal window value in windowSignal: " + self.options[c.OPTIONS_WINDOW])

    def getFilterPrevState(self, prev_coordinates):
        if self.options[c.OPTIONS_FILTER] == c.NONE_FILTER:
            return None
        elif self.options[c.OPTIONS_FILTER] in c.FILTER_NAMES:
            return scipy.signal.lfiltic(1.0, self.filter_coefficients, prev_coordinates)
        else:
            raise ValueError("Illegal filter value in filterPrevState: " + self.options[c.OPTIONS_FILTER])

    def signalPipeline(self, signal, window):
        raise NotImplementedError("signalPipeline not implemented!")


class SignalPipeline(SignalProcessing):
    def signalPipeline(self, signal, window):
        detrended_signal = self.detrendSignal(signal)
        filtered_signal, self.filter_prev_state = self.filterSignal(detrended_signal, self.filter_prev_state)
        windowed_signal = self.windowSignal(filtered_signal, window)
        return windowed_signal


class PsdPipeline(SignalProcessing):
    def normaliseSpectrum(self, fft):
        if self.options[c.OPTIONS_NORMALISE]:
            return fft/sum(fft)
        else:
            return fft

    def takeLog10(self, fft):
        if self.options[c.OPTIONS_LOG10]:
            return np.log10(fft)
        else:
            return fft

    def signalPipeline(self, signal, window):
        detrended_signal = self.detrendSignal(signal)
        filtered_signal, self.filter_prev_state = self.filterSignal(detrended_signal, self.filter_prev_state)
        windowed_signal = self.windowSignal(filtered_signal, window)
        amplitude_spectrum = (np.abs(np.fft.rfft(windowed_signal))**2)[1:]
        # same as scipy.signal.periodogram(windowed_signal, c.HEADSET_FREQ)*length*64?
        normalised_spectrum = self.normaliseSpectrum(amplitude_spectrum)
        return self.takeLog10(normalised_spectrum)
