__author__ = 'Anti'

import scipy.signal
import constants as c


class SignalProcessing(object):
    def __init__(self, options, window_function, channel_count, filter_coefficients):
        self.options = options
        self.channel_count = channel_count
        self.window_function = window_function
        self.filter_coefficients = filter_coefficients
        self.breakpoints = None
        self.menu_key_to_scipy_key = {
            c.WINDOW_HANNING:  c.SCIPY_WINDOW_HANNING,
            c.WINDOW_HAMMING:  c.SCIPY_WINDOW_HAMMING,
            c.WINDOW_BLACKMAN: c.SCIPY_WINDOW_BLACKMAN,
            c.WINDOW_KAISER:   c.SCIPY_WINDOW_KAISER,
            c.WINDOW_BARTLETT: c.SCIPY_WINDOW_BARTLETT
        }

    def setWindowArguments(self, options):
        if options[c.OPTIONS_WINDOW] == c.WINDOW_KAISER:
            return c.SCIPY_WINDOW_KAISER, options[c.OPTIONS_ARG]
        else:
            return self.menu_key_to_scipy_key[options[c.OPTIONS_WINDOW]]

    def setWindowFunction(self, options):
        if options[c.OPTIONS_WINDOW] == c.WINDOW_NONE:
            return None
        else:
            return self.setWindowArguments(options)

    def setFilter(self, options):
        if options[c.OPTIONS_FILTER]:
            to_value = options[c.OPTIONS_TO]
            from_value = options[c.OPTIONS_FROM]
            num_taps = options[c.OPTIONS_TAPS]
            nyq = c.HEADSET_FREQ/2.0
            # Currently leaving textboxes blank is not permitted!
            # Maybe additional optionmenu should be added to choose lowpass, highpass etc.
            if from_value != "" and to_value != "":
                self.filter_coefficients = scipy.signal.firwin(num_taps, [from_value/nyq, to_value/nyq], pass_zero=False)
            elif to_value != "":
                self.filter_coefficients = scipy.signal.firwin(num_taps, to_value/nyq)
            elif from_value != "":
                self.filter_coefficients = scipy.signal.firwin(num_taps, from_value/nyq, pass_zero=False)
            else:
                print("Insert from and/or to value")
                self.filter_coefficients = None
        else:
            self.filter_coefficients = None

    def setDetrend(self, options):
        if options[c.OPTIONS_DETREND]:
            breakpoints = options[c.OPTIONS_BREAK]
            if breakpoints == 0:
                self.breakpoints = None
            else:
                breakpoints_list = []
                for i in range(breakpoints):
                    breakpoints_list.append(options[c.OPTIONS_STEP]/breakpoints*(i+1))
                self.breakpoints = breakpoints_list

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