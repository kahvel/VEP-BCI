__author__ = 'Anti'

from controllable_windows import ExtractionWindow
from signal_processing import FFT
from main_logic import Abstract
import Tkinter
import numpy as np
from scipy import interpolate


class PSDAExtraction(ExtractionWindow.ExtractionWindow):
    def __init__(self, title):
        ExtractionWindow.ExtractionWindow.__init__(self, title)
        self.results_list = {"PSDA": []}

    def generator(self, index):
        coordinates_generators = [self.getCoordGenerator() for _ in range(self.getCoordGenCount())]
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
                self.connection.send("PSDA")
                main_generator.next()


def getMagnitude(freq, h_start, h_end, interpolation):
    result = 0
    for harmonic in range(h_start, h_end+1):
        result += interpolation(freq*harmonic)
    return result


def getSNR(freq, h_start, h_end, interpolation):
    result = 0
    for harmonic in range(h_start, h_end+1):
        harmonic_freq = freq*harmonic
        result += interpolation(harmonic_freq)*2/(interpolation(harmonic_freq-1)+interpolation(harmonic_freq+1))
    return result


def getMax(getValue, h_start, h_end, interpolation, target_freqs, max_list=None):
    max = 0
    max_index = -1
    for i in range(len(target_freqs)):
        ratio = getValue(target_freqs[i], h_start, h_end, interpolation)
        if max_list is not None:
            max_list[-1].append(ratio)
        if ratio > max:
            max = ratio
            max_index = i
    return max, max_index


def mainGenerator(length, step, sampling_freq, coordinates_generators, target_freqs, textbox, max_list=None):
    coord_gen_count = len(coordinates_generators)
    coordinates = [None for _ in range(coord_gen_count)]
    calculate_indices = True
    for generator in coordinates_generators:
        generator.send(None)
    while True:
        max_freqs = [0 for _ in range(len(target_freqs))]
        j = 0
        while j != coord_gen_count:
            for channel in range(coord_gen_count):
                y = yield
                result = coordinates_generators[channel].send(y)
                if result is not None:
                    coordinates[channel] = result
                    j += 1
                    coordinates_generators[channel].next()
        ps_len = len(coordinates[0])
        if calculate_indices:
            if ps_len == length//2+1:
                calculate_indices = False
            freq_indices = []
            for freq in target_freqs:
                index = int(freq*(ps_len-1)*2/sampling_freq)
                freq_indices.append(index)
                freqs = np.fft.rfftfreq((ps_len-1)*2)*sampling_freq
        if max_list is not None:
            max_list.append([])
        for channel in range(coord_gen_count):
            interpolation_fun = interpolate.interp1d(freqs, coordinates[channel])
            actual_max, max_index = getMax(getMagnitude, 1, 2, interpolation_fun, target_freqs, max_list)
            # print actual_max, sum(coordinates[channel])/len(coordinates[channel])*2+1
            # if sum(coordinates[channel])/len(coordinates[channel])*2+1 < actual_max:
            #     max_freqs[max_index] += 1
            max_freqs[max_index] += 1
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(actual_max)+"  ")
            maximum, max_index = getMax(getMagnitude, 2, 2, interpolation_fun, target_freqs)
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(maximum)+"  ")
            maximum, max_index = getMax(getMagnitude, 3, 3, interpolation_fun, target_freqs)
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(maximum)+"\n")
            maximum, max_index = getMax(getSNR, 1, 1, interpolation_fun, target_freqs)
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(maximum)+"  ")
            maximum, max_index = getMax(getSNR, 2, 2, interpolation_fun, target_freqs)
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(maximum)+"  ")
            maximum, max_index = getMax(getSNR, 3, 3, interpolation_fun, target_freqs)
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(maximum)+"\n\n")
            textbox.yview(Tkinter.END)
        for i in range(len(max_freqs)):
            if max_freqs[i] >= coord_gen_count:
                yield target_freqs[i]


class Single(Abstract.Single, PSDAExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        PSDAExtraction.__init__(self, "Sum Power Spectrum Density Analysis")

    def getCoordGenCount(self):
        return 1

    def getCoordGenerator(self):
        return FFT.Sum(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class Multiple(Abstract.Single, PSDAExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        PSDAExtraction.__init__(self, "Power Spectrum Density Analysis")

    def getCoordGenCount(self):
        return self.channel_count

    def getCoordGenerator(self):
        return FFT.NotSum(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()