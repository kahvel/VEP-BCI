from generators import AbstractGenerator

import constants as c

import scipy.signal
import numpy as np


class SignalPipelineGenerator(AbstractGenerator.AbstractPythonGenerator):
    def __init__(self, signalPipeline):
        """
        Superclass of all the signal coordinates pipeline generators. Takes raw EEG packets through yield and yields
        processed signal ready for feature extraction.
        :param signalPipeline: Signal pipeline function defined in SignalProcessing.SignalPipeline and
        SignalProcessing.PsdPipeline.
        :return:
        """
        AbstractGenerator.AbstractPythonGenerator.__init__(self)
        self.signalPipeline = signalPipeline
        self.yieldShortSignalResults = None
        self.options = None
        self.window_function = None
        self.menu_key_to_scipy_key = {
            c.WINDOW_HANNING:  c.SCIPY_WINDOW_HANNING,
            c.WINDOW_HAMMING:  c.SCIPY_WINDOW_HAMMING,
            c.WINDOW_BLACKMAN: c.SCIPY_WINDOW_BLACKMAN,
            c.WINDOW_KAISER:   c.SCIPY_WINDOW_KAISER,
            c.WINDOW_BARTLETT: c.SCIPY_WINDOW_BARTLETT
        }

    def setup(self, options):
        AbstractGenerator.AbstractPythonGenerator.setup(self, options)
        self.yieldShortSignalResults = options[c.DATA_PROCESS_SHORT_SIGNAL]
        self.window_function = self.getWindowFunction(options[c.DATA_OPTIONS], options[c.DATA_OPTIONS][c.OPTIONS_LENGTH])
        self.options = options[c.DATA_OPTIONS]

    def getWindowFunction(self, options, length):
        if options[c.OPTIONS_WINDOW] == c.WINDOW_NONE:
            return None
        elif options[c.OPTIONS_WINDOW] in c.WINDOW_FUNCTION_NAMES:
            return scipy.signal.get_window(self.getWindowWithArgs(options), length)
        else:
            raise ValueError("Illegal window value in getWindowFunction: " + options[c.OPTIONS_WINDOW])

    def getWindowWithArgs(self, options):
        if options[c.OPTIONS_WINDOW] == c.WINDOW_KAISER:
            return c.SCIPY_WINDOW_KAISER, options[c.OPTIONS_ARG]
        else:
            return self.menu_key_to_scipy_key[options[c.OPTIONS_WINDOW]]

    def processSignal(self, signal, segment, i, k):
        """
        Function used for processing signal. Takes the not updated signal and new segment of the signal and updates the
        signal.
        :param signal: Signal obtained in previous steps as list.
        :param segment: The signal segment obtained in the last step.
        :param i: The number of the segment between 0 and length/step-1 included. Good if the signal is cycling,
        for example in cycling averaging
        :param k: How many signals that have length length have been given to the function in total. Basically just
        counter (for averaging).
        :return: Updated and processed signal as list.
        """
        raise NotImplementedError("processSignal not implemented!")

    def processShortSignal(self, signal, i):
        """
        Similar to processSignal, but with fewer arguments. Used if it is desired that also shorter signals are
        processed (for example, the signal length is chosen 256 and step 32, then signals of length
        32, 64, ... are also processed and the generator does not wait until signal of length 256 is aquired).
        :param signal: Signal obtained in previous steps as list.
        :param i: The number of the segment between 0 and length/step-1 included. Good if the signal is cycling,
        for example in cycling averaging
        :return: Updated and processed signal as list.
        """
        raise NotImplementedError("processShortSignal not implemented!")

    def signalPipeline(self, signal, window):
        """
        Function that is called in the processSignal and processShortSignal functions as last step. The result of this
        function is returned from the previous functions. Not overridden, it is given as argument to constructor.
        :param signal: Updated signal.
        :param window: Window function.
        :return: Processed signal.
        """
        raise NotImplementedError("signalPipeline not implemented!")


class Generator(SignalPipelineGenerator):
    def __init__(self, signalPipeline):
        SignalPipelineGenerator.__init__(self, signalPipeline)

    def getGenerator(self, options):
        step = options[c.DATA_OPTIONS][c.OPTIONS_STEP]
        length = options[c.DATA_OPTIONS][c.OPTIONS_LENGTH]
        signal = []
        for i in range(length/step):
            segment = []
            for j in range(step):
                y = yield
                segment.append(y)
            signal.extend(segment)
            if self.yieldShortSignalResults:
                yield self.processShortSignal(signal, i)
        if not self.yieldShortSignalResults:
            yield self.processShortSignal(signal, i)
        counter = 1
        while True:
            counter += 1
            for i in range(length/step):
                segment = []
                for j in range(step):
                    y = yield
                    segment.append(float(y))
                yield self.processSignal(signal, segment, i, counter)


class SumGenerator(SignalPipelineGenerator):
    def __init__(self, signalPipeline):
        SignalPipelineGenerator.__init__(self, signalPipeline)
        self.generators = None

    def setup(self, options):
        self.generators = []
        for _ in range(len(options[c.DATA_SENSORS])):
            generator = self.getInnerGenerator()
            generator.setup(options)
            self.generators.append(generator)
        SignalPipelineGenerator.setup(self, options)

    def getInnerGenerator(self):
        raise NotImplementedError("getInnerGenerator not implemented!")

    def processSignal(self, sum_of_signals, *args):
        """
        Override to describe different parameters.
        :param sum_of_signals: Signals summed together from different inner generators (for example different sensors).
        :param args: Dummy args to match superclass method signature.
        :return: Processed signal
        """
        raise NotImplementedError("processSignal not implemented!")

    def getGenerator(self, options):
        while True:
            signals = []
            for generator in self.generators:
                y = yield
                signals.append(generator.send(y))
            if None not in signals:
                sum_of_signals = np.mean(signals, axis=0)
                result = self.processSignal(sum_of_signals)
                yield result
                for generator in self.generators:
                    generator.next()


class SumAverageSignalGenerator(SumGenerator):
    def getInnerGenerator(self):
        return SumAverageSignalInnerGenerator()

    def processSignal(self, sum_of_signals, *args):
        return self.signalPipeline(sum_of_signals, self.window_function)


class SumSignalGenerator(SumGenerator):
    def getInnerGenerator(self):
        return SumSignalInnerGenerator()

    def processSignal(self, sum_of_signals, *args):
        return self.signalPipeline(sum_of_signals, self.getWindowFunction(self.options, len(sum_of_signals)))


class AverageSignalGenerator(Generator):
    def __init__(self, signalPipeline):
        Generator.__init__(self, signalPipeline)

    def getSegment(self, array, i):
        if array is not None:
            step = self.options[c.OPTIONS_STEP]
            return array[i*step:i*step+step]
        else:
            return None

    def processSignal(self, signal, segment, i, k):
        step = len(segment)
        for j in range(step):
            signal[i*step+j] = (signal[i*step+j] * (k - 1) + segment[j]) / k
        return self.signalPipeline(signal, self.window_function)

    def processShortSignal(self, signal, i):
        return self.signalPipeline(signal, self.getSegment(self.window_function, i))


class SignalGenerator(Generator):
    def __init__(self, signalPipeline):
        Generator.__init__(self, signalPipeline)

    def processSignal(self, signal, segment, i, k):
        signal.extend(segment)
        del signal[:len(segment)]
        return self.signalPipeline(signal, self.window_function)

    def processShortSignal(self, signal, i):
        return self.signalPipeline(signal, self.getWindowFunction(self.options, len(signal)))


class SumSignalInnerGenerator(SignalGenerator):
    def __init__(self):
        SignalGenerator.__init__(self, self.signalPipeline)

    def signalPipeline(self, signal, window):
        """
        Signal pipeline always returns just the signal. The sum generator then processes the signal as required.
        :param signal: Updated signal.
        :param window: Window function.
        :return: Same signal as argument.
        """
        return signal


class SumAverageSignalInnerGenerator(AverageSignalGenerator):
    def __init__(self):
        AverageSignalGenerator.__init__(self, self.signalPipeline)

    def signalPipeline(self, signal, window):
        """
        Signal pipeline always returns just the signal. The sum generator then processes the signal as required.
        :param signal: Updated signal.
        :param window: Window function.
        :return: Same signal as argument.
        """
        return signal
