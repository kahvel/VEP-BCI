__author__ = 'Anti'

from controllable_windows import ExtractionWindow
from signal_processing import Signal, FFT
from main_logic import Abstract, CCAExtraction, PSDAExtraction


class CCAPSDAExtraction(ExtractionWindow.ExtractionWindow):
    def __init__(self, title):
        ExtractionWindow.ExtractionWindow.__init__(self, title)
        self.result_lists = {"CCA": [], "PSDA": [], "short CCA": [], "short PSDA": []}

    def getShortCoordGenerator(self, length):
        raise NotImplementedError("getShortCoordCount not implemented")

    def copyDict(self, length):
        options = self.options.copy()  # shallow copy
        options["Length"] = length
        return options

    def generator(self, index):
        self.result_lists = {"CCA": [], "PSDA": [], "short CCA": [], "short PSDA": []}
        coordinates_generators = [Signal.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator() for _ in range(self.channel_count)]
        cca_generator = CCAExtraction.mainGenerator(self.options["Length"], self.options["Step"], self.headset_freq,
                                                    coordinates_generators, self.freq_points, self.canvas,
                                                    self.result_lists["CCA"])
        cca_generator.send(None)
        coordinates_generators = [self.getCoordGenerator() for _ in range(self.getCoordGenCount())]
        psda_generator = PSDAExtraction.mainGenerator(self.options["Length"], self.options["Step"], self.headset_freq,
                                                      coordinates_generators, self.freq_points, self.canvas,
                                                      self.result_lists["PSDA"])
        psda_generator.send(None)
        short_length = 64
        options = self.copyDict(short_length)
        coordinates_generators = [Signal.MultipleRegular(options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator() for _ in range(self.channel_count)]
        short_cca_generator = CCAExtraction.mainGenerator(options["Length"], self.options["Step"], self.headset_freq,
                                                          coordinates_generators, self.freq_points, self.canvas,
                                                          self.result_lists["short CCA"])
        short_cca_generator.send(None)
        coordinates_generators = [self.getShortCoordGenerator(short_length) for _ in range(self.getCoordGenCount())]
        short_psda_generator = PSDAExtraction.mainGenerator(options["Length"], self.options["Step"], self.headset_freq,
                                                            coordinates_generators, self.freq_points, self.canvas,
                                                            self.result_lists["short PSDA"])
        short_psda_generator.send(None)
        i = 0
        result_count = 1
        prev_result = [None for _ in range(result_count)]
        short_result_count = 2
        short_prev_result = [None for _ in range(short_result_count)]
        while True:
            i += 1
            coordinate = yield
            cca_result = cca_generator.send(coordinate)
            psda_result = psda_generator.send(coordinate)
            short_cca_result = short_cca_generator.send(coordinate)  # TODO maybe shift calculation by step/2
            short_psda_result = short_psda_generator.send(coordinate)
            if short_cca_result is not None or short_psda_result is not None or cca_result is not None or psda_result is not None:
                print i, cca_result, psda_result, short_cca_result, short_psda_result
            if psda_result is not None and cca_result is not None:
                if cca_result == psda_result:
                    prev_result.append(cca_result)
                    del prev_result[0]
                    if prev_result[1:] == prev_result[:-1]:
                        # prev_result = [None for _ in range(result_count)]
                        self.connection.send(cca_result)
                        self.connection.send("CCAPSDA")
                else:
                    # if short_cca_result == short_psda_result:
                    #     short_prev_result.append(short_cca_result)
                    #     del short_prev_result[0]
                    #     if short_prev_result[1:] == short_prev_result[:-1]:
                    #         self.connection.send(short_cca_result)
                    #         self.connection.send("CCAPSDA")
                    # else:
                    #     short_prev_result.append(None)
                    #     del short_prev_result[0]
                    prev_result.append(None)
                    del prev_result[0]
            if cca_result is not None:
                cca_generator.next()
            if psda_result is not None:
                psda_generator.next()
            if short_cca_result is not None:
                short_cca_generator.next()
            if short_psda_result is not None:
                short_psda_generator.next()


class Single(Abstract.Single, CCAPSDAExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        CCAPSDAExtraction.__init__(self, "CCA and PSDA Extraction method")

    def getCoordGenCount(self):
        return 1

    def getCoordGenerator(self):
        return FFT.SingleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()

    def getShortCoordGenerator(self, length):
        options = self.copyDict(length)
        return FFT.SingleRegular(options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class Multiple(Abstract.Single, CCAPSDAExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        CCAPSDAExtraction.__init__(self, "CCA and PSDA Extraction method")

    def getCoordGenCount(self):
        return self.channel_count

    def getCoordGenerator(self):
        return FFT.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()

    def getShortCoordGenerator(self, length):
        options = self.copyDict(length)
        return FFT.SingleRegular(options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()