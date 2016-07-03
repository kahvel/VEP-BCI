import constants as c


class AbstractGenerator(object):
    def __init__(self):
        self.generator = None

    def setup(self, options):
        self.generator = self.getGenerator(options)

    def getGenerator(self, options):
        raise NotImplementedError("getGenerator not implemented!")

    def send(self, message):
        return self.generator.send(message)

    def next(self):
        self.generator.next()


class AbstractPythonGenerator(AbstractGenerator):
    def setup(self, options):
        AbstractGenerator.setup(self, options)
        self.generator.send(None)


class AbstractMyGenerator(AbstractGenerator):
    def setup(self, options):
        AbstractGenerator.setup(self, options)
        self.generator.setup(options)


class AbstractExtracionGenerator(AbstractPythonGenerator):
    def __init__(self):
        AbstractPythonGenerator.__init__(self)
        self.harmonics = None
        self.short_signal = None

    def setup(self, options):
        AbstractPythonGenerator.setup(self, options)
        self.harmonics = self.getHarmonics(options)
        self.short_signal = True

    def getHarmonics(self, options):
        return options[c.DATA_HARMONICS]

    def checkLength(self, signal_length, options_length):
        if self.short_signal and signal_length == options_length:
            self.short_signal = False
