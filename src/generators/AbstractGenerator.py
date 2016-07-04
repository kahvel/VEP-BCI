

class AbstractGenerator(object):
    def __init__(self):
        self.generator = None

    def setup(self, options):
        self.generator = self.getGenerator(options)

    def getGenerator(self, options):
        raise NotImplementedError("getGenerator not implemented!")

    def send(self, message):
        raise NotImplementedError("getGenerator not implemented!")

    def next(self):
        raise NotImplementedError("next not implemented!")


class SingleGenerator(AbstractGenerator):
    def send(self, message):
        return self.generator.send(message)

    def next(self):
        self.generator.next()


class AbstractPythonGenerator(SingleGenerator):
    def setup(self, options):
        SingleGenerator.setup(self, options)
        self.generator.send(None)


class AbstractMyGenerator(SingleGenerator):
    def setup(self, options):
        SingleGenerator.setup(self, options)
        self.generator.setup(options)


class AbstractExtracionGenerator(AbstractPythonGenerator):
    def __init__(self):
        AbstractPythonGenerator.__init__(self)
        self.short_signal = None
        self.ranker = None

    def setup(self, options):
        AbstractPythonGenerator.setup(self, options)
        self.short_signal = True
        self.ranker.setup(options)

    def checkLength(self, actual_length, max_length):
        if self.short_signal and actual_length == max_length:
            self.short_signal = False
        return self.short_signal