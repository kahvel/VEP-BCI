__author__ = 'Anti'

import numpy as np
import constants as c


class AbstractPythonGenerator(object):
    def __init__(self):
        self.generator = None

    def setup(self, options):
        self.generator = self.getGenerator(options)
        self.generator.send(None)

    def getGenerator(self, options):
        raise NotImplementedError("getGenerator not implemented!")

    def send(self, message):
        return self.generator.send(message)

    def next(self):
        self.generator.next()


class AbstractMyGenerator(AbstractPythonGenerator):
    def __init__(self):
        AbstractPythonGenerator.__init__(self)

    def setup(self, options):
        self.generator = self.getGenerator(options)
        self.generator.setup(options)


class Generator(AbstractPythonGenerator):
    def __init__(self, processSignal, processShortSignal, signalPipeline):
        AbstractPythonGenerator.__init__(self)
        self.processSignal = processSignal
        self.processShortSignal = processShortSignal
        self.signalPipeline = signalPipeline

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
            yield self.processShortSignal(signal, i, self.signalPipeline)
        counter = 1
        while True:
            counter += 1
            for i in range(length/step):
                segment = []
                for j in range(step):
                    y = yield
                    segment.append(float(y))
                yield self.processSignal(signal, segment, i, counter, self.signalPipeline)


class SumGenerator(Generator):
    def __init__(self, innerProcessSignal, innerProcessShortSignal, innerSignalPipeline, sumPipeline, processSumSignals):
        Generator.__init__(self, innerProcessSignal, innerProcessShortSignal, innerSignalPipeline)
        self.generators = None
        self.sumPipeline = sumPipeline
        self.processSumSignals = processSumSignals

    def setup(self, options):
        self.generators = []
        for _ in range(len(options[c.DATA_SENSORS])):
            generator = Generator(self.processSignal, self.processShortSignal, self.signalPipeline)
            generator.setup(options)
            self.generators.append(generator)
        AbstractPythonGenerator.setup(self, options)

    def getGenerator(self, options):
        while True:
            signals = []
            for generator in self.generators:
                y = yield
                signals.append(generator.send(y))
            if None not in signals:
                sum_of_signals = np.mean(signals, axis=0)
                result = self.processSumSignals(sum_of_signals, self.sumPipeline)
                yield result
                for generator in self.generators:
                    generator.next()


class AbstractExtracionGenerator(AbstractPythonGenerator):
    def __init__(self):
        AbstractPythonGenerator.__init__(self)
        self.harmonics = None
        self.short_signal = None

    def setup(self, options):
        AbstractPythonGenerator.setup(self, options)
        self.harmonics = self.getHarmonics(options[c.DATA_OPTIONS])
        self.short_signal = True

    def getHarmonics(self, options):
        return options[c.OPTIONS_HARMONICS]

    def getMax(self, getValue, arg_list):
        max_value = -float("inf")
        max_index = None
        for i in range(len(arg_list)):
            value = getValue(arg_list[i])
            if value > max_value:
                max_value = value
                max_index = i
        return max_value, max_index

    def checkLength(self, signal_length, options_length):
        if self.short_signal and signal_length == options_length:
            self.short_signal = False
