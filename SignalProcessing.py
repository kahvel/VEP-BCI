__author__ = 'Anti'
import scipy.signal


class SignalProcessing(object):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        self.options = options
        self.channel_count = channel_count
        self.window_function = window_function
        self.filter_coefficients = filter_coefficients

    def filterSignal(self, signal, filter_prev_state):
        if self.options["Filter"]:
            return scipy.signal.lfilter(self.filter_coefficients, 1.0, signal, zi=filter_prev_state)
        else:
            return signal, None

    def detrendSignal(self, signal):
        if self.options["Detrend"]:
            return scipy.signal.detrend(signal, bp=self.options["Breakpoints"])
        else:
            return scipy.signal.detrend(signal, type="constant")

    def windowSignal(self, signal, window):
        if self.options["Window"]:
            return signal*window
        else:
            return signal

    def filterPrevState(self, prev_coordinates):
        if self.options["Filter"]:
            return scipy.signal.lfiltic(1.0, self.filter_coefficients, prev_coordinates)
        else:
            return None


class Multiple(object):
    def getPlotCount(self, channel_count):
        return channel_count


class Single(object):
    def getPlotCount(self, channel_count):
        return 1