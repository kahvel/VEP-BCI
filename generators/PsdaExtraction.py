__author__ = 'Anti'

import numpy as np
import scipy.interpolate
import constants as c
from generators import Generator


class PsdaExtraction(Generator.AbstractPythonGenerator):
    def __init__(self):
        Generator.AbstractPythonGenerator.__init__(self)

    def getMagnitude(self, freq, h_start, h_end, interpolation):
        result = 0
        for harmonic in range(h_start, h_end+1):
            result += interpolation(freq*harmonic)
        return result

    def getSNR(self, freq, h_start, h_end, interpolation):
        result = 0
        for harmonic in range(h_start, h_end+1):
            harmonic_freq = freq*harmonic
            result += interpolation(harmonic_freq)*2/(interpolation(harmonic_freq-1)+interpolation(harmonic_freq+1))
        return result

    def getMax(self, getValue, h_start, h_end, interpolation, target_freqs):
        max = 0
        max_index = -1
        for i in range(len(target_freqs)):
            ratio = getValue(target_freqs[i], h_start, h_end, interpolation)
            if ratio > max:
                max = ratio
                max_index = i
        return max, max_index

    def getGenerator(self, options):
        length = options[c.DATA_OPTIONS][c.OPTIONS_LENGTH]
        target_freqs = options[c.DATA_FREQS]
        calculate_indices = True
        while True:
            coordinates = yield
            if calculate_indices:
                ps_len = len(coordinates)
                if ps_len == length//2+1:
                    calculate_indices = False
                freqs = np.fft.rfftfreq((ps_len-1)*2)*c.HEADSET_FREQ
            interpolation_fun = scipy.interpolate.interp1d(freqs, coordinates)
            actual_max, max_index = self.getMax(self.getMagnitude, 1, 2, interpolation_fun, target_freqs)
            # print actual_max, sum(coordinates[channel])/len(coordinates[channel])*2+1
            # if sum(coordinates[channel])/len(coordinates[channel])*2+1 < actual_max:
            #     max_freqs[max_index] += 1
            yield target_freqs[max_index]
