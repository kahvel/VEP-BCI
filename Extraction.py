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
        self.main_generators = None
        self.coordinates_generators = None
        self.connection.waitMessages(self.start, lambda: None, lambda: None, self.setup)

    def start(self):
        while True:
            message = self.connection.receiveMessagePoll(0.1)
            if isinstance(message, basestring):
                return message
            if message is not None:
                for sensor, coordinates_generator, main_generator in zip(self.sensors, self.coordinates_generators, self.main_generators):
                    coordinates = coordinates_generator.send(message.sensors[sensor]["value"])
                    if coordinates is not None:
                        coordinates_generator.next()
                        result = main_generator.send(coordinates)
                        if result is not None:
                            self.connection.sendMessage(result)
                            self.connection.sendMessage("PSDA")
                            main_generator.next()

    def setup(self):
        self.sensors, options, target_freqs = self.connection.receiveOptions()
        self.coordinates_generators = self.getCoordinatesGenerators(options, len(self.sensors))
        self.main_generators = self.getMainGenerator(
            options[c.DATA_OPTIONS],
            target_freqs,
            len(self.sensors)
        )
        return c.SUCCESS_MESSAGE

    def setupGenerator(self, options):
        generator_class = self.getGeneratorClass(options)
        """ @type : Signal.Signal | FFT.FFT """
        generator_class.setup(options)
        coordinates_generator = generator_class.coordinates_generator()
        coordinates_generator.send(None)
        return coordinates_generator

    def setupMainGenerator(self, options, target_freqs):
        generator = self.mainGenerator(options[c.OPTIONS_LENGTH], target_freqs)
        generator.send(None)
        return generator

    def getGeneratorClass(self, options):
        raise NotImplementedError("getGeneratorClass not implemented!")

    def mainGenerator(self, *args):
        raise NotImplementedError("mainGenerator not implemented!")

    def getCoordinatesGenerators(self, options, sensor_count):
        raise NotImplementedError("getCoordinatesGenerators not implemented!")

    def getMainGenerator(self, options, target_freqs, sensor_count):
        raise NotImplementedError("getMainGenerator not implemented!")


class NotSum(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection)

    def getCoordinatesGenerators(self, options, sensor_count):
        return [self.setupGenerator(options) for _ in range(sensor_count)]

    def getMainGenerator(self, options, target_freqs, sensor_count):
        return [self.setupMainGenerator(options, target_freqs) for _ in range(sensor_count)]


class Sum(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection)

    def getCoordinatesGenerators(self, options, sensor_count):
        generator = self.setupGenerator(options)
        return [generator for _ in range(sensor_count)]

    def getMainGenerator(self, options, target_freqs, sensor_count):
        generator = self.setupMainGenerator(options, target_freqs)
        return [generator for _ in range(sensor_count)]


class SumPsdaExtraction(Sum):
    def __init__(self, connection):
        Sum.__init__(self, connection)

    def getGeneratorClass(self, options):
        return FFT.Sum()

    def mainGenerator(self, length, target_freqs):
        return PsdaExtraction.mainGenerator(length, target_freqs)


class NotSumPsdaExtraction(NotSum):
    def __init__(self, connection):
        NotSum.__init__(self, connection)

    def getGeneratorClass(self, options):
        return FFT.NotSum()

    def mainGenerator(self, length, target_freqs):
        return PsdaExtraction.mainGenerator(length, target_freqs)


class NotSumCcaExtraction(NotSum):
    def __init__(self, connection):
        NotSum.__init__(self, connection)

    def getGeneratorClass(self, options):
        return Signal.NotSum()

    def mainGenerator(self, length, step, headset_freq, coordinates_generators, target_freqs):
        return CcaExtraction.mainGenerator(length, step, headset_freq, coordinates_generators, target_freqs)


class NotSumCcaPsdaExtraction(NotSum):
    def __init__(self, connection):
        NotSum.__init__(self, connection)

    def getGeneratorClass(self, options):
        return Both.NotSum()


class SumCcaPsdaExtraction(NotSum):
    def __init__(self, connection):
        NotSum.__init__(self, connection)

    def getGeneratorClass(self, options):
        return Both.Sum()
