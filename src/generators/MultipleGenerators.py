from generators.coordinates import Signal, PSD
import constants as c
import AbstractGenerator


class AbstractMultipleGenerators(AbstractGenerator.AbstractGenerator):
    def __init__(self):
        AbstractGenerator.AbstractGenerator.__init__(self)
        self.sensors = None

    def setup(self, options):
        AbstractGenerator.AbstractGenerator.setup(self, options)
        self.sensors = self.getSensors(options)
        self.setupGenerators(options)

    def getSensors(self, options):
        return options[c.DATA_SENSORS]

    def setupGenerators(self, options):
        raise NotImplementedError("setupGenerators not implemented!")


class MultipleGenerators(AbstractMultipleGenerators):
    def setupGenerators(self, options):
        for generator in self.generator:
            generator.setup(options)

    def send(self, message):
        for generator, sensor in zip(self.generator, self.sensors):
            yield generator, generator.send(message[sensor])

    def next(self):
        for generator in self.generator:
            generator.next()


class MultipleSignalGenerators(MultipleGenerators):
    def getGenerator(self, options):
        return [Signal.Signal() for _ in self.getSensors(options)]


class MultiplePsdGenerators(MultipleGenerators):
    def getGenerator(self, options):
        return [PSD.PSD() for _ in self.getSensors(options)]


class MultipleSignalPsdGenerators(AbstractMultipleGenerators):
    def __init__(self):
        AbstractMultipleGenerators.__init__(self)
        self.generator_keys = ("Signal", "PSDA")

    def setupGenerators(self, options):
        for key in self.generator_keys:
            for generator in self.generator[key]:
                generator.setup(options)

    def send(self, message):
        for key in self.generator_keys:
            for generator, sensor in zip(self.generator[key], self.sensors):
                yield generator, generator.send(message[sensor])

    def next(self):
        for key in self.generator_keys:
            for generator in self.generator[key]:
                generator.next()

    def getGenerator(self, options):
        return {
            "Signal": [Signal.Signal() for _ in self.getSensors(options)],
            "PSDA": [PSD.PSD() for _ in self.getSensors(options)]
        }
