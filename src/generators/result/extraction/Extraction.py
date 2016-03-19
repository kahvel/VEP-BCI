import constants as c
from generators import Generator
from generators.result.extraction import CcaExtraction, PsdaExtraction
from generators.coordinates import Signal, PSD


class Extraction(Generator.AbstractMyGenerator):
    def __init__(self, connection, name):
        Generator.AbstractMyGenerator.__init__(self)
        self.connection = connection
        """ @type : ConnectionProcessEnd.ExtractionConnection """
        self.name = name
        self.sensors = None
        self.coordinates_generator = None
        self.target_freqs = None
        self.options = None
        # self.pw = pg.plot()
        self.connection.waitMessages(self.start, self.exit, lambda: None, self.setup)

    def exit(self):
        self.connection.close()

    # def update(self):
    #     pg.QtGui.QApplication.processEvents()

    def start(self):
        while True:
            # self.updateWindow()
            message = self.connection.receiveMessageInstant()
            if message == c.CLEAR_BUFFER_MESSAGE:
                self.setupCoordinatesGenerator()
                self.generator = self.getGenerator(self.options) # this and next line needed for processing short signals
                self.generator.setup(self.options)
            elif isinstance(message, basestring):
                return message
            elif message is not None:
                for sensor in self.sensors:
                    coordinates = self.coordinates_generator.send(message[sensor])
                if coordinates is not None:
                    self.coordinates_generator.next()
                    result = self.generator.send(coordinates)
                    self.connection.sendMessage(result)
                    self.generator.next()
                else:
                    self.connection.sendMessage(None)

    def setupCoordinatesGenerator(self): # Used for resetting and setting up the generator (options has to be attribute)
        self.coordinates_generator = self.getCoordinatesGenerator()
        self.coordinates_generator.setup(self.options)

    def setup(self, options=None):
        self.options = self.connection.receiveOptions()
        self.sensors = tuple(self.options[c.DATA_SENSORS])
        self.setupCoordinatesGenerator()
        Generator.AbstractMyGenerator.setup(self, self.options)
        return c.SUCCESS_MESSAGE

    def getCoordinatesGenerator(self):
        raise NotImplementedError("getCoordinatesGenerator not implemented!")


class SumPsda(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection, c.SUM_PSDA)

    def getCoordinatesGenerator(self):
        return PSD.SumPsd()

    def getGenerator(self, options):
        return PsdaExtraction.PsdaExtraction()


class Psda(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection, c.PSDA)

    def getCoordinatesGenerator(self):
        return PSD.PSD()

    def getGenerator(self, options):
        return PsdaExtraction.PsdaExtraction()


class Cca(Extraction):
    def __init__(self, connection):
        Extraction.__init__(self, connection, c.CCA)
        self.coordinates_generators = None

    def getCoordinatesGenerator(self):
        return [Signal.Signal() for _ in range(len(self.sensors))]

    def getGenerator(self, options):
        return CcaExtraction.CcaExtraction()

    def setup(self, options=None):
        self.options = self.connection.receiveOptions()
        self.sensors = tuple(self.options[c.DATA_SENSORS])
        self.setupCoordinatesGenerator()
        Generator.AbstractMyGenerator.setup(self, self.options)
        return c.SUCCESS_MESSAGE

    def setupCoordinatesGenerator(self):
        self.coordinates_generators = self.getCoordinatesGenerator()
        for generator in self.coordinates_generators:
            generator.setup(self.options)

    def start(self):
        while True:
            # self.updateWindow()
            message = self.connection.receiveMessageInstant()
            if message == c.CLEAR_BUFFER_MESSAGE:
                self.setupCoordinatesGenerator()
                self.generator = self.getGenerator(self.options) # this and next line needed for processing short signals
                self.generator.setup(self.options)
            elif isinstance(message, basestring):
                return message
            elif message is not None:
                results = None
                for sensor, generator in zip(self.sensors, self.coordinates_generators):
                    signal = generator.send(message[sensor])
                    if signal is not None:
                        generator.next()
                        results = self.generator.send(signal)
                if results is not None:
                    self.connection.sendMessage(results)
                    self.generator.next()
                else:
                    self.connection.sendMessage(None)
