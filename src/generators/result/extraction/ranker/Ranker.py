import constants as c
from generators.result import Logic


class Ranker(object):
    def __init__(self):
        pass

    def getRanking(self, results):
        return sorted(results, key=lambda x: x[1], reverse=True)

    def getResults(self, coordinates, target_freqs):
        raise NotImplementedError("getResults not implemented!")

    def setup(self, options):
        raise NotImplementedError("setup not implemented!")


class RankerWithHarmonics(Ranker):
    def __init__(self):
        Ranker.__init__(self)
        self.harmonics = None

    def setup(self, options):
        self.harmonics = self.getHarmonics(options)

    def getHarmonics(self, options):
        return options[c.DATA_HARMONICS]


class RankerWithReferenceSignals(RankerWithHarmonics):
    def __init__(self):
        Ranker.__init__(self)
        self.reference_handler = Logic.ReferenceSignals()

    def setup(self, options):
        RankerWithHarmonics.setup(self, options)
        self.reference_handler.setup(options)
