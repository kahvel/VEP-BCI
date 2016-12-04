from generators.coordinates import SignalProcessing, Generator


class AverageSignal(SignalProcessing.SignalPipeline):
    def __init__(self):
        SignalProcessing.SignalPipeline.__init__(self)

    def getGenerator(self, options):
        return Generator.AverageSignalGenerator(self.signalPipeline)


class Signal(SignalProcessing.SignalPipeline):
    def __init__(self):
        SignalProcessing.SignalPipeline.__init__(self)

    def getGenerator(self, options):
        return Generator.SignalGenerator(self.signalPipeline)


class SumSignal(SignalProcessing.SignalPipeline):
    def __init__(self):
        SignalProcessing.SignalPipeline.__init__(self)

    def getGenerator(self, options):
        return Generator.SumSignalGenerator(self.signalPipeline)


class SumAverageSignal(SignalProcessing.SignalPipeline):
    def __init__(self):
        SignalProcessing.SignalPipeline.__init__(self)

    def getGenerator(self, options):
        return Generator.SumAverageSignalGenerator(self.signalPipeline)


