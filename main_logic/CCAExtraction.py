__author__ = 'Anti'

from controllable_windows import ExtractionWindow
from signal_processing import Signal
from main_logic import Abstract
import Tkinter
import numpy as np
import sklearn.cross_decomposition


class CCAExtraction(ExtractionWindow.ExtractionWindow):
    def __init__(self, title):
        ExtractionWindow.ExtractionWindow.__init__(self, title)
        self.results_list = {"CCA": []}

    def generator(self, index):
        coordinates_generators = [self.getCoordGenerator() for _ in range(self.channel_count)]
        main_generator = mainGenerator(self.options["Length"], self.options["Step"], self.headset_freq,
                                       coordinates_generators, self.freq_points, self.canvas)
        main_generator.send(None)
        i = 0
        while True:
            i += 1
            coordinate = yield
            result = main_generator.send(coordinate)
            if result is not None:
                self.connection.send(result)
                self.connection.send("CCA")
                main_generator.next()

    def getCoordGenerator(self):
        return Signal.Sum(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


def mainGenerator(length, step, sampling_freq, coordinates_generators, target_freqs, textbox, max_list=None):
    get_segment = True
    coord_gen_count = len(coordinates_generators)
    h = 3  # number of harmonics
    target_signals = []
    t = np.arange(0, length)
    for freq in target_freqs:
        target_signals.append([])
        for harmonic in range(1, h+1):
            target_signals[-1].append(np.sin(np.pi*2*harmonic*freq/sampling_freq*t))
            target_signals[-1].append(np.cos(np.pi*2*harmonic*freq/sampling_freq*t))
    cca = sklearn.cross_decomposition.CCA(n_components=1)
    for generator in coordinates_generators:
        generator.send(None)
    coordinates = [None for _ in range(coord_gen_count)]
    while True:
        for j in range(length/step):
            # print coordinates
            i = 0
            while i != coord_gen_count:
                for channel in range(coord_gen_count):
                    y = yield
                    result = coordinates_generators[channel].send(y)
                    if result is not None:
                        coordinates[channel] = np.roll(result, -(j+1)*step)
                        i += 1
                        coordinates_generators[channel].next()
            maximum = 0
            max_index = 0
            if max_list is not None:
                max_list.append([])
            for i in range(len(target_signals)):
                if get_segment:
                    signal_segment = np.array([target_signals[i][j][:len(coordinates[0])] for j in range(len(target_signals[i]))]).T
                    if len(coordinates) == length:
                        get_segment = False
                    res_x, res_y = cca.fit_transform(np.array(coordinates).T, signal_segment)
                else:
                    res_x, res_y = cca.fit_transform(np.array(coordinates).T, target_signals[i].T)
                corr = np.corrcoef(res_x.T, res_y.T)[0][1]
                if max_list is not None:
                    max_list[-1].append(corr)
                if corr > maximum:
                    maximum = corr
                    max_index = i
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(maximum)+"\n")
            # print maximum, 0.2
            # if maximum > 0.2:
            #     yield target_freqs[max_index]
            yield target_freqs[max_index]


class Single(Abstract.Single, CCAExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        CCAExtraction.__init__(self, "Canonical Correlation Analysis")


class Multiple(Abstract.Single, CCAExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        CCAExtraction.__init__(self, "Canonical Correlation Analysis")