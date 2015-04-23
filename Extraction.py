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
        self.main_generator = None
        self.coordinates_generator = None
        self.target_freqs = None
        # self.pw = pg.plot()
        self.connection.waitMessages(self.start, self.exit, lambda: None, self.setup)

    def exit(self):
        self.connection.closeConnection()

    # def update(self):
    #     pg.QtGui.QApplication.processEvents()

    def start(self):
        while True:
            # self.updateWindow()
            message = self.connection.receiveMessagePoll(0.1)
            if isinstance(message, basestring):
                return message
            if message is not None:
                for sensor in self.sensors:
                    coordinates = self.coordinates_generator.send(message.sensors[sensor]["value"])
                if coordinates is not None:
                    self.coordinates_generator.next()
                    result = self.main_generator.send(coordinates)
                    self.connection.sendMessage(result)
                    self.main_generator.next()
                else:
                    self.connection.sendMessage(None)

    def setup(self):
        self.sensors, options, target_freqs = self.connection.receiveOptions()
        self.coordinates_generator = self.setupGenerator(self.getGenerator(), options)
        self.main_generator = self.getMainGenerator(
            options[c.DATA_OPTIONS][c.OPTIONS_LENGTH],
            options[c.DATA_OPTIONS][c.OPTIONS_STEP],
            target_freqs,
            len(self.sensors)
        )
        self.main_generator.send(None)
        return c.SUCCESS_MESSAGE

    def setupGenerator(self, generator, options):
        generator.setup(options)
        return generator

    def getGenerator(self):
        raise NotImplementedError("getGenerator not implemented!")

    def getMainGenerator(self, length, step, target_freqs, generator_count):
        raise NotImplementedError("getMainGenerator not implemented!")


class SumPsda(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection, c.SUM_PSDA)

    def getGenerator(self):
        return PSD.SumPsd()

    def getMainGenerator(self, length, step, target_freqs, generator_count):
        return PsdaExtraction.mainGenerator(length, target_freqs)


class Psda(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection, c.SUM_PSDA)

    def getGenerator(self):
        return PSD.PSD()

    def getMainGenerator(self, length, step, target_freqs, generator_count):
        return PsdaExtraction.mainGenerator(length, target_freqs)


class Cca(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection, c.SUM_PSDA)

    def getGenerator(self):
        return Signal.Signal()

    def getMainGenerator(self, length, step, target_freqs, generator_count):
        return CcaExtraction.mainGenerator(length, step, target_freqs, generator_count)
