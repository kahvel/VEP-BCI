from generators.coordinates import SignalProcessing, Generator


class PSD(SignalProcessing.PsdPipeline):
    def __init__(self):
        SignalProcessing.PsdPipeline.__init__(self)

    def getGenerator(self, options):
        return Generator.SignalGenerator(self.signalPipeline)


class AveragePSD(SignalProcessing.PsdPipeline):
    def __init__(self):
        SignalProcessing.PsdPipeline.__init__(self)

    def getGenerator(self, options):
        return Generator.AverageSignalGenerator(self.signalPipeline)


class SumAveragePSD(SignalProcessing.PsdPipeline):
    def __init__(self):
        SignalProcessing.PsdPipeline.__init__(self)

    def getGenerator(self, options):
        return Generator.SumAverageSignalGenerator(self.signalPipeline)


class SumPsd(SignalProcessing.PsdPipeline):
    def __init__(self):
        SignalProcessing.PsdPipeline.__init__(self)

    def getGenerator(self, options):
        return Generator.SumSignalGenerator(self.signalPipeline)
