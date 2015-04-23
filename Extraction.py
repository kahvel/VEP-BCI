__author__ = 'Anti'

import constants as c
from signal_processing import Signal, PSD
import PsdaExtraction
import CcaExtraction
import pyqtgraph as pg


class Extraction(object):
    def __init__(self, connection, name):
        self.connection = connection
        """ @type : ConnectionProcessEnd.ExtractionConnection """
        self.name = name
        self.sensors = None
        self.main_generators = None
        self.coordinates_generators = None
        self.target_freqs = None
        # self.pw = pg.plot()
        self.connection.waitMessages(self.start, self.exit, lambda: None, self.setup)

    def exit(self):
        self.connection.closeConnection()

    # def update(self):
    #     pg.QtGui.QApplication.processEvents()

    def start(self):
        while True:
            # self.update()
            message = self.connection.receiveMessagePoll(0.1)
            if isinstance(message, basestring):
                return message
            if message is not None:
                results = {freq: 0 for freq in self.target_freqs}
                for sensor, coordinates_generator, main_generator in zip(self.sensors, self.coordinates_generators, self.main_generators):
                    coordinates = coordinates_generator.send(message.sensors[sensor]["value"])
                    if coordinates is not None:
                        # self.pw.plot(coordinates, clear=True)
                        coordinates_generator.next()
                        result = main_generator.send(coordinates)
                        if result is not None:
                            results[result] += 1
                            main_generator.next()
                max_result = max(results.items(), key=lambda x: x[1])
                if max_result[1] >= len(set(self.main_generators)):
                    self.connection.sendMessage((max_result[0], self.name))
                else:
                    self.connection.sendMessage((None, None))

    def setup(self):
        sensors, options, self.target_freqs = self.connection.receiveOptions()
        self.coordinates_generators = self.getGenerators(options, len(sensors))
        self.main_generators = self.getMainGenerators(
            options[c.DATA_OPTIONS],
            self.target_freqs,
            len(sensors)
        )
        self.sensors = self.getSensors(sensors)
        return c.SUCCESS_MESSAGE

    def setupCoordinatesGenerator(self, options, generator):
        generator.setup(options)
        return generator

    def setupGenerator(self, generator):
        generator.send(None)
        return generator

    def getGenerator(self):
        raise NotImplementedError("getGenerator not implemented!")

    def getMainGenerator(self, *args):
        raise NotImplementedError("getMainGenerator not implemented!")

    def getGenerators(self, options, sensor_count):
        raise NotImplementedError("getGenerators not implemented!")

    def getMainGenerators(self, options, target_freqs, sensor_count):
        raise NotImplementedError("getMainGenerators not implemented!")

    def getSensors(self, sensors):
        return sensors


class NotSum(Extraction):
    def __init__(self, connection, name):
        Extraction.__init__(self, connection, name)

    def getGenerators(self, options, sensor_count):
        return [self.setupCoordinatesGenerator(options, self.getGenerator()) for _ in range(sensor_count)]

    def getMainGenerators(self, options, target_freqs, sensor_count):
        return [self.setupGenerator(self.getMainGenerator(options, target_freqs, sensor_count)) for _ in range(sensor_count)]


class Sum(Extraction):
    def __init__(self, connection, name):
        Extraction.__init__(self, connection, name)

    def getGenerators(self, options, sensor_count):
        generator = self.setupCoordinatesGenerator(options, self.getGenerator())
        return [generator for _ in range(sensor_count)]

    def getMainGenerators(self, options, target_freqs, sensor_count):
        generator = self.setupGenerator(self.getMainGenerator(options, target_freqs, sensor_count))
        return [generator for _ in range(sensor_count)]


class SumPsdaExtraction(Sum):
    def __init__(self, connection):
        Sum.__init__(self, connection, c.SUM_PSDA)

    def getGenerator(self):
        return PSD.SumPsd()

    def getMainGenerator(self, options, target_freqs, generator_count):
        return PsdaExtraction.mainGenerator(options[c.OPTIONS_LENGTH], target_freqs)


class NotSumPsdaExtraction(NotSum):
    def __init__(self, connection):
        NotSum.__init__(self, connection, c.PSDA)

    def getGenerator(self):
        return PSD.PSD()

    def getMainGenerator(self, options, target_freqs, generator_count):
        return PsdaExtraction.mainGenerator(options[c.OPTIONS_LENGTH], target_freqs)


class NotSumCcaExtraction(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection, c.CCA)

    def getMainGenerator(self, options, target_freqs, generator_count):
        return CcaExtraction.mainGenerator(options[c.OPTIONS_LENGTH], options[c.OPTIONS_STEP], target_freqs, generator_count)

    def getMainGenerators(self, options, target_freqs, sensor_count):
        generator = self.setupGenerator(self.getMainGenerator(options, target_freqs, sensor_count))
        return [generator for _ in range(sensor_count)]

    def getGenerators(self, options, sensor_count):
        return [self.setupCoordinatesGenerator(options, Signal.Signal()) for _ in range(sensor_count)]


class CcaPsdaExtraction(Extraction):
    def __init__(self, connection, name):
        Extraction.__init__(self, connection, name)

    def getCcaGenerator(self, options, target_freqs, generator_count):
        return CcaExtraction.mainGenerator(options[c.OPTIONS_LENGTH], options[c.OPTIONS_STEP], target_freqs, generator_count)

    def getPsdaGenerator(self, options, target_freqs):
        return PsdaExtraction.mainGenerator(options[c.OPTIONS_LENGTH], target_freqs)

    def getSensors(self, sensors):
        return sensors*2


class SumCcaPsdaExtraction(CcaPsdaExtraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection, c.SUM_BOTH)

    def getGenerator(self):
        return PSD.SumPsd()

    def getMainGenerators(self, options, target_freqs, generator_count):
        cca_generator = self.setupGenerator(self.getCcaGenerator(options, target_freqs, generator_count))
        psda_generator = self.setupGenerator(self.getPsdaGenerator(options, target_freqs))
        return [cca_generator for _ in range(generator_count)] +\
               [psda_generator for _ in range(generator_count)]

    def getGenerators(self, options, sensor_count):
        sum_psd_generator = self.setupCoordinatesGenerator(options, self.getGenerator())
        return [self.setupCoordinatesGenerator(options, Signal.Signal()) for _ in range(sensor_count)] +\
               [sum_psd_generator for _ in range(sensor_count)]


class NotSumCcaPsdaExtraction(CcaPsdaExtraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection, c.BOTH)

    def getGenerator(self):
        return PSD.PSD()

    def getMainGenerators(self, options, target_freqs, generator_count):
        cca_generator = self.setupGenerator(self.getCcaGenerator(options, target_freqs, generator_count))
        return [cca_generator for _ in range(generator_count)] +\
               [self.setupGenerator(self.getPsdaGenerator(options, target_freqs)) for _ in range(generator_count)]

    def getGenerators(self, options, sensor_count):
        return [self.setupCoordinatesGenerator(options, Signal.Signal()) for _ in range(sensor_count)] +\
               [self.setupCoordinatesGenerator(options, self.getGenerator()) for _ in range(sensor_count)]
