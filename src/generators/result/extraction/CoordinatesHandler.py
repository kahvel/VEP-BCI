import constants as c
from generators import AbstractGenerator
from generators.result.extraction.ranker import CorrelationRanker, PsdRanker, PsdaSnrRanker

import numpy as np


class MultipleCoordinatesGeneratorHandler(AbstractGenerator.AbstractExtracionGenerator):
    def __init__(self):
        """
        The class which Extraction uses to extract features. Extraction receives messages and sends it here.
        This class does all the processing using self.ranker and sends back the extracted features (correlation with
        reference signals).
        :return:
        """
        AbstractGenerator.AbstractExtracionGenerator.__init__(self)

    def getGenerator(self, options):
        generator_count = len(options[c.DATA_SENSORS])
        target_freqs = options[c.DATA_FREQS].values()
        coordinates = [[] for _ in range(generator_count)]
        while True:
            for i in range(generator_count):
                coordinates[i] = yield
            yield self.ranker.getResults(coordinates, target_freqs)


class CcaExtraction(MultipleCoordinatesGeneratorHandler):
    def __init__(self):
        MultipleCoordinatesGeneratorHandler.__init__(self)
        self.model = None
        self.ranker = CorrelationRanker.CcaRanker()


class LrtExtraction(MultipleCoordinatesGeneratorHandler):
    def __init__(self):
        MultipleCoordinatesGeneratorHandler.__init__(self)
        self.ranker = CorrelationRanker.LrtRanker()


class PsdaSnrExtraction(MultipleCoordinatesGeneratorHandler):
    def __init__(self):
        MultipleCoordinatesGeneratorHandler.__init__(self)
        self.ranker = PsdaSnrRanker.PsdaSnrRanker()

    # def getGenerator(self, options):  # Removed after realising PSDA SNR does not need PSDA coordinates.
    #     max_length = options[c.DATA_OPTIONS][c.OPTIONS_LENGTH]
    #     generator_count = len(options[c.DATA_SENSORS])
    #     target_freqs = options[c.DATA_FREQS].values()
    #     coordinates = {
    #         "Signal": [[] for _ in range(generator_count)],
    #         "PSDA": [[] for _ in range(generator_count)]
    #     }
    #     while True:
    #         for i in range(generator_count):
    #             coordinates["Signal"][i] = yield
    #         for i in range(generator_count):
    #             coordinates["PSDA"][i] = yield
    #         actual_length = len(coordinates["Signal"][0])
    #         is_short = self.checkLength(actual_length, max_length)
    #         yield self.ranker.getResults(coordinates, actual_length, target_freqs, is_short)


class PsdaExtraction(AbstractGenerator.AbstractExtracionGenerator):
    def __init__(self):
        AbstractGenerator.AbstractExtracionGenerator.__init__(self)
        self.ranker = PsdRanker.PsdRanker()

    def getGenerator(self, options):
        target_freqs = options[c.DATA_FREQS].values()
        while True:
            coordinates = yield
            yield self.ranker.getResults(coordinates, target_freqs)
