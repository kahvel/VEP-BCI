__author__ = 'Anti'

import scipy.signal
import constants as c
from generators import Generator
import numpy as np


class SignalProcessing(Generator.AbstractMyGenerator):
    def __init__(self):
        Generator.AbstractMyGenerator.__init__(self)
        self.options = None
        self.channels = None
        self.window_function = None
        self.filter_coefficients = None
        self.breakpoints = None
        self.filter_prev_state = None
        self.menu_key_to_scipy_key = {
            c.WINDOW_HANNING:  c.SCIPY_WINDOW_HANNING,
            c.WINDOW_HAMMING:  c.SCIPY_WINDOW_HAMMING,
            c.WINDOW_BLACKMAN: c.SCIPY_WINDOW_BLACKMAN,
            c.WINDOW_KAISER:   c.SCIPY_WINDOW_KAISER,
            c.WINDOW_BARTLETT: c.SCIPY_WINDOW_BARTLETT
        }

    def setup(self, options):
        Generator.AbstractMyGenerator.setup(self, options)
        self.options = options[c.DATA_OPTIONS]
        self.window_function = self.getWindowFunction(self.options, self.options[c.OPTIONS_LENGTH])
        self.filter_coefficients = self.getFilter(self.options)
        self.breakpoints = self.getBreakpoints(self.options)
        self.filter_prev_state = self.getFilterPrevState([0])

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
            breakpoints_count = options[c.OPTIONS_BREAK]+1
            breakpoints_list = []
            for i in range(breakpoints_count):
                breakpoints_list.append(options[c.OPTIONS_LENGTH]/breakpoints_count*i)
            return breakpoints_list
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

    def getShortBreakpoints(self, signal):
        return [breakpoint for breakpoint in self.breakpoints if breakpoint < len(signal)]

    def detrendSignal(self, signal):
        if self.options[c.OPTIONS_DETREND] == c.LINEAR_DETREND:
            return scipy.signal.detrend(signal, type="linear", bp=self.getShortBreakpoints(signal))
        elif self.options[c.OPTIONS_DETREND] == c.CONSTANT_DETREND:
            return scipy.signal.detrend(signal, type="constant", bp=self.getShortBreakpoints(signal))
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

    def getFilterPrevState(self, prev_coordinates):
        if self.options[c.OPTIONS_FILTER] == c.NONE_FILTER:
            return None
        elif self.options[c.OPTIONS_FILTER] in c.FILTER_NAMES:
            return scipy.signal.lfiltic(1.0, self.filter_coefficients, prev_coordinates)
        else:
            raise ValueError("Illegal filter value in filterPrevState: " + self.options[c.OPTIONS_FILTER])


class SignalPipeline(SignalProcessing):
    def __init__(self, signalPipeline):
        SignalProcessing.__init__(self)
        self.signalPipeline = signalPipeline

    def getSegment(self, array, i):
        if array is not None:
            step = self.options[c.OPTIONS_STEP]
            return array[i*step:i*step+step]
        else:
            return None

    def normaliseSpectrum(self, fft):
        if self.options[c.OPTIONS_NORMALISE]:
            result = (fft/sum(fft))[1:]
            return result
        else:
            result = np.log10(fft)[1:]
            return result

    def innerPipeline(self, signal, window):
        raise NotImplementedError("innerPipeline not implemented!")

    def processSumSignals(self, signal, pipelineFunction):
        raise NotImplementedError("processSumSignals not implemented!")

    def processSignal(self, signal, segment, i, k, pipelineFunction):
        raise NotImplementedError("processSignal not implemented!")

    def processShortSignal(self, signal, i, pipelineFunction):
        raise NotImplementedError("processShortSignal not implemented!")


class AverageSignal(SignalPipeline):
    def __init__(self, signalPipeline):
        SignalPipeline.__init__(self, signalPipeline)

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


class Signal(SignalPipeline):
    def __init__(self, signalPipeline):
        SignalPipeline.__init__(self, signalPipeline)

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
    def __init__(self, signalPipeline):
        Signal.__init__(self, signalPipeline)

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
        return pipelineFunction(signal, self.getWindowFunction(self.options, len(signal)))


class SumAverageSignal(AverageSignal):
    def __init__(self, signalPipeline):
        AverageSignal.__init__(self, signalPipeline)

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
