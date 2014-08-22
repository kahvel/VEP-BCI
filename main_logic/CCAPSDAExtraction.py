__author__ = 'Anti'

from controllable_windows import ExtractionWindow
from signal_processing import Signal, FFT
from main_logic import Abstract, CCAExtraction, PSDAExtraction


class CCAPSDAExtraction(ExtractionWindow.ExtractionWindow):
    def __init__(self, title):
        ExtractionWindow.ExtractionWindow.__init__(self, title)

    def getGenerator(self, index):
        return self.generator(index)

    def generator(self, index):
        coordinates_generators = [Signal.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator() for _ in range(self.channel_count)]
        cca_generator = CCAExtraction.mainGenerator(self.options["Length"], self.options["Step"], self.headset_freq,
                                                    coordinates_generators, self.freq_points, self.canvas)
        cca_generator.send(None)
        coordinates_generators = [self.getCoordGenerator() for _ in range(self.getCoordGenCount())]
        psda_generator = PSDAExtraction.mainGenerator(self.options["Length"], self.options["Step"], self.headset_freq,
                                                      coordinates_generators, self.freq_points, self.canvas)
        psda_generator.send(None)
        i = 0
        while True:
            i += 1
            coordinate = yield
            cca_result = cca_generator.send(coordinate)
            psda_result = psda_generator.send(coordinate)
            if cca_result is not None or psda_result is not None:
                print i, cca_result, psda_result
            if psda_result is not None:
                if cca_result == psda_result:
                    self.connection.send(cca_result)
                    self.connection.send("CCAPSDA")
                cca_generator.next()
                psda_generator.next()


class Single(Abstract.Single, CCAPSDAExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        CCAPSDAExtraction.__init__(self, "CCA and PSDA Extraction method")

    def getCoordGenCount(self):
        return 1

    def getCoordGenerator(self):
        return FFT.SingleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class Multiple(Abstract.Single, CCAPSDAExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        CCAPSDAExtraction.__init__(self, "CCA and PSDA Extraction method")

    def getCoordGenCount(self):
        return self.channel_count

    def getCoordGenerator(self):
        return FFT.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()