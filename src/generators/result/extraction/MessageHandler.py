import constants as c
from generators import AbstractGenerator, MultipleGenerators
from generators.result.extraction import CoordinatesHandler
from generators.coordinates import PSD


class MessageHandler(AbstractGenerator.AbstractMyGenerator):
    def __init__(self, connection, name):
        """
        Class that handles messages. First messages are received, then sent to coordinates generators, then the
        result from coordinates generator is sent to extraction generators.
        :param connection:
        :param name:
        :return:
        """
        AbstractGenerator.AbstractMyGenerator.__init__(self)
        self.connection = connection
        self.name = name
        self.sensors = None
        self.target_freqs = None
        self.options = None
        self.coordinates_generator = None
        self.debug = False
        self.counter = None
        # self.pw = pg.plot()
        self.connection.waitMessages(self.start, self.exit, lambda: None, self.setup)

    def exit(self):
        self.connection.close()

    def start(self):
        while True:
            # self.updateWindow()
            message = self.connection.receiveMessageInstant()
            if message == c.CLEAR_BUFFER_MESSAGE:
                self.setupCoordinatesGenerator()
                AbstractGenerator.AbstractMyGenerator.setup(self, self.options)  # needed for processing short signals
            elif isinstance(message, basestring):
                return message
            elif message is not None:
                self.printMessage(message, 0)
                self.handleEegMessage(message)

    def handleEegMessage(self, message):
        raise NotImplementedError("handleEegMessage not implemented!")

    def setup(self, options=None):
        """
        :param options: Always none because otherwise it is not possible to call setup without arguments in
        ConnectionProcessEnd waitMessages method. On the other hand it is subclass of AbstractMyGenerator whose setup
        does take an argument. Options are received via connection.
        :return:
        """
        self.counter = {key: 0 for key in range(5)}
        self.options = self.connection.receiveOptions()
        self.sensors = tuple(self.options[c.DATA_SENSORS])
        self.setupCoordinatesGenerator()
        AbstractGenerator.AbstractMyGenerator.setup(self, self.options)
        return c.SUCCESS_MESSAGE

    def setupCoordinatesGenerator(self): # Used for resetting and setting up the generator (options has to be attribute)
        self.coordinates_generator = self.getCoordinatesGenerator()
        self.coordinates_generator.setup(self.options)

    def getCoordinatesGenerator(self):
        raise NotImplementedError("getCoordinatesGenerator not implemented!")

    def printMessage(self, message, key):
        if self.debug:
            self.counter[key] += 1
            if message is not None:
                print self.counter[key], message

    # def update(self):
    #     pg.QtGui.QApplication.processEvents()


class SingleCoordinatesGeneratorHandler(MessageHandler):
    def __init__(self, connection, name):
        MessageHandler.__init__(self, connection, name)
        self.coordinates_generator = None

    def handleEegMessage(self, message):
        coordinates = None
        for sensor in self.sensors:
            coordinates = self.coordinates_generator.send(message[sensor])
        if coordinates is not None:
            self.printMessage(coordinates, 1)
            self.coordinates_generator.next()
            result = self.generator.send(coordinates)
            self.printMessage(result, 2)
            self.connection.sendMessage(result)
            self.generator.next()
        else:
            self.connection.sendMessage(None)


class SumPsda(SingleCoordinatesGeneratorHandler):
    def __init__(self, connection):
        SingleCoordinatesGeneratorHandler.__init__(self, connection, c.SUM_PSDA)

    def getCoordinatesGenerator(self):
        return PSD.SumPsd()

    def getGenerator(self, options):
        return CoordinatesHandler.PsdaExtraction()


class Psda(SingleCoordinatesGeneratorHandler):
    def __init__(self, connection):
        SingleCoordinatesGeneratorHandler.__init__(self, connection, c.PSDA)

    def getCoordinatesGenerator(self):
        return PSD.PSD()

    def getGenerator(self, options):
        return CoordinatesHandler.PsdaExtraction()


class MultipleCoordinatesGeneratorHandler(MessageHandler):
    def __init__(self, connection, name):
        MessageHandler.__init__(self, connection, name)

    def handleEegMessage(self, message):
        results = None
        for generator, response in self.coordinates_generator.send(message):
            if response is not None:
                self.printMessage(response, 1)
                generator.next()
                results = self.generator.send(response)
        if results is not None:
            self.printMessage(results, 2)
            self.connection.sendMessage(results)
            self.generator.next()
        else:
            self.connection.sendMessage(None)


class CCA(MultipleCoordinatesGeneratorHandler):
    def __init__(self, connection):
        MultipleCoordinatesGeneratorHandler.__init__(self, connection, c.CCA)

    def getGenerator(self, options):
        return CoordinatesHandler.CcaExtraction()

    def getCoordinatesGenerator(self):
        return MultipleGenerators.MultipleSignalGenerators()


class LRT(MultipleCoordinatesGeneratorHandler):
    def __init__(self, connection):
        MultipleCoordinatesGeneratorHandler.__init__(self, connection, c.LRT)

    def getGenerator(self, options):
        return CoordinatesHandler.LrtExtraction()

    def getCoordinatesGenerator(self):
        return MultipleGenerators.MultipleSignalGenerators()


class PsdaSnrMethod(MultipleCoordinatesGeneratorHandler):
    def __init__(self, connection):
        MultipleCoordinatesGeneratorHandler.__init__(self, connection, c.SNR_PSDA)

    def getGenerator(self, options):
        return CoordinatesHandler.PsdaSnrExtraction()

    def getCoordinatesGenerator(self):
        return MultipleGenerators.MultipleSignalPsdGenerators()
