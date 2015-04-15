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
        sensors, options, target_freqs = self.connection.receiveOptions()
        self.sensors = self.getSensors(sensors)
        self.coordinates_generators = self.getCoordinatesGenerators(options, len(self.sensors))
        self.main_generators = self.getMainGenerator(
            options[c.DATA_OPTIONS],
            target_freqs,
            len(self.sensors)
        )
        return c.SUCCESS_MESSAGE

    def setupCoordinatesGenerator(self, options, generator_class):
        generator_class.setup(options)
        coordinates_generator = generator_class.coordinates_generator()
        return self.setupGenerator(coordinates_generator)

    def setupGenerator(self, generator):
        generator.send(None)
        return generator

    def getGeneratorClass(self):
        raise NotImplementedError("getGeneratorClass not implemented!")

    def mainGenerator(self, *args):
        raise NotImplementedError("mainGenerator not implemented!")

    def getCoordinatesGenerators(self, options, sensor_count):
        raise NotImplementedError("getCoordinatesGenerators not implemented!")

    def getMainGenerator(self, options, target_freqs, sensor_count):
        raise NotImplementedError("getMainGenerator not implemented!")

    def getSensors(self, sensors):
        return sensors


class NotSum(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection)

    def getCoordinatesGenerators(self, options, sensor_count):
        return [self.setupCoordinatesGenerator(options, self.getGeneratorClass()) for _ in range(sensor_count)]

    def getMainGenerator(self, options, target_freqs, sensor_count):
        return [self.setupGenerator(self.mainGenerator(options, target_freqs, sensor_count)) for _ in range(sensor_count)]


class Sum(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection)

    def getCoordinatesGenerators(self, options, sensor_count):
        generator = self.setupCoordinatesGenerator(options, self.getGeneratorClass())
        return [generator for _ in range(sensor_count)]

    def getMainGenerator(self, options, target_freqs, sensor_count):
        generator = self.setupGenerator(self.mainGenerator(options, target_freqs, sensor_count))
        return [generator for _ in range(sensor_count)]


class SumPsdaExtraction(Sum):
    def __init__(self, connection):
        Sum.__init__(self, connection)

    def getGeneratorClass(self):
        return FFT.Sum()

    def mainGenerator(self, options, target_freqs, generator_count):
        return PsdaExtraction.mainGenerator(options[c.OPTIONS_LENGTH], target_freqs)


class NotSumPsdaExtraction(NotSum):
    def __init__(self, connection):
        NotSum.__init__(self, connection)

    def getGeneratorClass(self):
        return FFT.NotSum()

    def mainGenerator(self, options, target_freqs, generator_count):
        return PsdaExtraction.mainGenerator(options[c.OPTIONS_LENGTH], target_freqs)


class NotSumCcaExtraction(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection)

    def mainGenerator(self, options, target_freqs, generator_count):
        return CcaExtraction.mainGenerator(options[c.OPTIONS_LENGTH], options[c.OPTIONS_STEP], target_freqs, generator_count)

    def getMainGenerator(self, options, target_freqs, sensor_count):
        generator = self.setupGenerator(self.mainGenerator(options, target_freqs, sensor_count))
        return [generator for _ in range(sensor_count)]

    def getCoordinatesGenerators(self, options, sensor_count):
        return [self.setupCoordinatesGenerator(options, Signal.NotSum()) for _ in range(sensor_count)]


class CcaPsdaExtraction(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection)

    def getCcaGenerator(self, options, target_freqs, generator_count):
        return CcaExtraction.mainGenerator(options[c.OPTIONS_LENGTH], options[c.OPTIONS_STEP], target_freqs, generator_count)

    def getPsdaGenerator(self, options, target_freqs):
        return PsdaExtraction.mainGenerator(options[c.OPTIONS_LENGTH], target_freqs)

    def getMainGenerator(self, options, target_freqs, generator_count):
        cca_generator = self.setupGenerator(self.getCcaGenerator(options, target_freqs, generator_count))
        return [cca_generator for _ in range(generator_count)]+\
               [self.setupGenerator(self.getPsdaGenerator(options, target_freqs)) for _ in range(generator_count)]

    def getCoordinatesGenerators(self, options, sensor_count):
        return [self.setupCoordinatesGenerator(options, Signal.NotSum()) for _ in range(sensor_count)]+\
               [self.setupCoordinatesGenerator(options, self.getGeneratorClass()) for _ in range(sensor_count)]

    def getSensors(self, sensors):
        return sensors*2


class SumCcaPsdaExtraction(CcaPsdaExtraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection)

    def getGeneratorClass(self):
        return FFT.Sum()


class NotSumCcaPsdaExtraction(CcaPsdaExtraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection)

    def getGeneratorClass(self):
        return FFT.NotSum()