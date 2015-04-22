__author__ = 'Anti'

import scipy.signal
import constants as c


class SignalProcessing(object):
    def __init__(self):
        self.options = None
        self.channels = None
        self.window_function = None
        self.filter_coefficients = None
        self.breakpoints = None
        self.menu_key_to_scipy_key = {
            c.WINDOW_HANNING:  c.SCIPY_WINDOW_HANNING,
            c.WINDOW_HAMMING:  c.SCIPY_WINDOW_HAMMING,
            c.WINDOW_BLACKMAN: c.SCIPY_WINDOW_BLACKMAN,
            c.WINDOW_KAISER:   c.SCIPY_WINDOW_KAISER,
            c.WINDOW_BARTLETT: c.SCIPY_WINDOW_BARTLETT
        }

    def setup(self, options):
        self.window_function = self.getWindowFunction(options, options[c.OPTIONS_LENGTH])
        self.filter_coefficients = self.getFilter(options)
        self.breakpoints = self.getBreakpoints(options)
        self.options = options

    def getWindowWithArgs(self, options):
        if options[c.OPTIONS_WINDOW] == c.WINDOW_KAISER:
            return c.SCIPY_WINDOW_KAISER, options[c.OPTIONS_ARG]
        else:
            return self.menu_key_to_scipy_key[options[c.OPTIONS_WINDOW]]

    def getWindowFunction(self, options, length):
        if options[c.OPTIONS_WINDOW] == c.WINDOW_NONE:
            return None
        elif options[c.OPTIONS_WINDOW] in c.WINDOW_FUNCTION_NAMES:
            return scipy.signal.get_window(self.getWindowWithArgs(options), length)
        else:
            raise ValueError("Illegal window value in getWindowFunction: " + options[c.OPTIONS_WINDOW])

    def getFilter(self, options):
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
        elif options[c.OPTIONS_FILTER] == c.NONE_FILTER:
            return None
        else:
            raise ValueError("Illegal filter value in getFilter: " + options[c.OPTIONS_FILTER])

    def getBreakpoints(self, options):
        if options[c.OPTIONS_DETREND] in (c.LINEAR_DETREND, c.CONSTANT_DETREND):
            breakpoints = options[c.OPTIONS_BREAK]
            if breakpoints != 0:
                breakpoints_list = []
                for i in range(breakpoints):
                    breakpoints_list.append(options[c.OPTIONS_STEP]/breakpoints*(i+1))
                return breakpoints_list
            else:
                return 0
        elif options[c.OPTIONS_DETREND] == c.NONE_DETREND:
            return 0
        else:
            raise ValueError("Illegal detrend value in getBreakpoints: " + options[c.OPTIONS_DETREND])

    def filterSignal(self, signal, filter_prev_state):
        if self.options[c.OPTIONS_FILTER] == c.NONE_FILTER:
            return signal, None
        elif self.options[c.OPTIONS_FILTER] in c.FILTER_NAMES:
            return scipy.signal.lfilter(self.filter_coefficients, 1.0, signal, zi=filter_prev_state)
        else:
            raise ValueError("Illegal filter value in filterSignal: " + self.options[c.OPTIONS_FILTER])

    def detrendSignal(self, signal):
        if self.options[c.OPTIONS_DETREND] == c.LINEAR_DETREND:
            return scipy.signal.detrend(signal, type="linear", bp=self.options[c.OPTIONS_BREAK])
        elif self.options[c.OPTIONS_DETREND] == c.CONSTANT_DETREND:
            return scipy.signal.detrend(signal, type="constant", bp=self.options[c.OPTIONS_BREAK])
        elif self.options[c.OPTIONS_DETREND] == c.NONE_DETREND:
            return signal
        else:
            raise ValueError("Illegal detrend value in detrendSignal: " + self.options[c.OPTIONS_DETREND])

    def windowSignal(self, signal, window):
        if self.options[c.OPTIONS_WINDOW] == c.WINDOW_NONE:
            return signal
        elif self.options[c.OPTIONS_WINDOW] in c.WINDOW_FUNCTION_NAMES:
            return signal*window
        else:
            raise ValueError("Illegal window value in windowSignal: " + self.options[c.OPTIONS_WINDOW])

    def filterPrevState(self, prev_coordinates):
        if self.options[c.OPTIONS_FILTER] == c.NONE_FILTER:
            return None
        elif self.options[c.OPTIONS_FILTER] in c.FILTER_NAMES:
            return scipy.signal.lfiltic(1.0, self.filter_coefficients, prev_coordinates)
        else:
            raise ValueError("Illegal filter value in filterPrevState: " + self.options[c.OPTIONS_FILTER])
