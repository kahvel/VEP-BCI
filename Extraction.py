__author__ = 'Anti'

import constants as c
from signal_processing import Signal, FFT
import PsdaExtraction
import CcaExtraction


class Extraction(object):
    def __init__(self, connection):
        self.connection = connection
        """ @type : ConnectionProcessEnd.PlotConnection """
        self.pw = None
        self.sensors = None
        self.main_generator = None
        self.connection.waitMessages(self.start, lambda: None, lambda: None, self.setup)

    def start(self):
        while True:
            message = self.connection.receiveMessagePoll(0.1)
            if isinstance(message, basestring):
                return message
            if message is not None:
                for sensor in self.sensors:
                    result = self.main_generator.send(message.sensors[sensor]["value"])
                if result is not None:
                    self.connection.sendMessage(result)
                    self.connection.sendMessage("PSDA")
                    self.main_generator.next()

    def setup(self):
        self.sensors, options, target_freqs = self.connection.receiveOptions()
        coordinates_generator = [self.setupGenerator(options) for _ in range(len(self.sensors))]
        self.main_generator = self.setupMainGenerator(options[c.DATA_OPTIONS], coordinates_generator, target_freqs)
        self.main_generator.send(None)
        return c.SUCCESS_MESSAGE

    def setupGenerator(self, options):
        generator_class = self.getGeneratorClass(options)
        """ @type : Signal.Signal | FFT.FFT """
        generator_class.setup(options)
        coordinates_generator = generator_class.coordinates_generator()
        coordinates_generator.send(None)
        return coordinates_generator

    def setupMainGenerator(self, options, coordinates_generator, target_freqs):
        return self.mainGenerator(
            options[c.OPTIONS_LENGTH],
            options[c.OPTIONS_STEP],
            c.HEADSET_FREQ,
            coordinates_generator,
            target_freqs,
        )

    def getGeneratorClass(self, options):
        raise NotImplementedError("getGeneratorClass not implemented!")

    def mainGenerator(self, length, step, headset_freq, coordinates_generators, target_freqs):
        raise NotImplementedError("mainGenerator not implemented!")


class Sum(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection)


class NotSum(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection)


class NotSumPsdaExtraction(NotSum):
    def __init__(self, connection):
        NotSum.__init__(self, connection)

    def getGeneratorClass(self, options):
        return FFT.NotSum()

    def mainGenerator(self, length, step, headset_freq, coordinates_generators, target_freqs):
        return PsdaExtraction.mainGenerator(length, step, headset_freq, coordinates_generators, target_freqs)


class SumPsdaExtraction(Sum):
    def __init__(self, connection):
        Sum.__init__(self, connection)

    def getGeneratorClass(self, options):
        return FFT.Sum()

    def mainGenerator(self, length, step, headset_freq, coordinates_generators, target_freqs):
        return PsdaExtraction.mainGenerator(length, step, headset_freq, coordinates_generators, target_freqs)


class SumCcaExtraction(NotSum):
    def __init__(self, connection):
        NotSum.__init__(self, connection)

    def getGeneratorClass(self, options):
        return Signal.NotSum()

    def mainGenerator(self, length, step, headset_freq, coordinates_generators, target_freqs):
        return CcaExtraction.mainGenerator(length, step, headset_freq, coordinates_generators, target_freqs)


class SumCcaPsdaExtraction(Sum):
    def __init__(self, connection):
        Sum.__init__(self, connection)

    def getGeneratorClass(self, options):
        return Both.MultipleRegular()


class NotSumCcaPsdaExtraction(Sum):
    def __init__(self, connection):
        Sum.__init__(self, connection)

    def getGeneratorClass(self, options):
        return Both.SingleRegular()
