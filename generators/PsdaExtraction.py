__author__ = 'Anti'

import numpy as np
import scipy.interpolate
import constants as c
from generators import Generator


class PsdaExtraction(Generator.AbstractExtracionGenerator):
    def __init__(self):
        Generator.AbstractExtracionGenerator.__init__(self)
        self.interpolation = None
        self.fft_bins = None
        self.menu_key_to_scipy_key = {
            c.INTERPOLATE_LINEAR: c.SCIPY_INTERPOLATE_LINEAR,
            c.INTERPOLATE_NEAREST: c.SCIPY_INTERPOLATE_NEAREST,
            c.INTERPOLATE_ZERO: c.SCIPY_INTERPOLATE_ZERO,
            c.INTERPOLATE_CUBIC: c.SCIPY_INTERPOLATE_CUBIC,
            c.INTERPOLATE_SLINEAR: c.SCIPY_INTERPOLATE_SLINEAR,
            c.INTERPOLATE_QUADRATIC: c.SCIPY_INTERPOLATE_QUADRATIC
        }

    def setup(self, options):
        Generator.AbstractExtracionGenerator.setup(self, options)
        self.interpolation = self.getInterpolation(options[c.DATA_OPTIONS])
        self.fft_bins = np.fft.rfftfreq(options[c.DATA_OPTIONS][c.OPTIONS_LENGTH])[1:]*c.HEADSET_FREQ

    def getInterpolation(self, options):
        if options[c.OPTIONS_INTERPOLATE] in self.menu_key_to_scipy_key:
            return lambda x, y: scipy.interpolate.interp1d(x, y, kind=self.menu_key_to_scipy_key[options[c.OPTIONS_INTERPOLATE]])
        elif options[c.OPTIONS_INTERPOLATE] == c.INTERPOLATE_BARYCENTRIC:
            return lambda x, y: scipy.interpolate.BarycentricInterpolator(x, y)
        else:
            raise ValueError("Illegal argument in getInterpolation: " + str(options[c.OPTIONS_INTERPOLATE]))

    def getMagnitude(self, freq, harmonic_count, interpolation):
        result = 0
        for harmonic in range(harmonic_count):
            result += interpolation(freq*(harmonic+1))
        return result

    # def getSNR(self, freq, harmonic_count, interpolation):
    #     result = 0
    #     for harmonic in range(harmonic_count):
    #         harmonic_freq = freq*(harmonic+1)
    #         result += interpolation(harmonic_freq)*2/(interpolation(harmonic_freq-1)+interpolation(harmonic_freq+1))
    #     return result

    def getSignalLength(self, fft_length):
        return (fft_length)*2

    def getFftLength(self, signal_length):
        return signal_length//2

    def getFreqs(self, fft_length):
        if self.short_signal:
            return np.fft.rfftfreq(self.getSignalLength(fft_length))[1:]*c.HEADSET_FREQ
        else:
            return self.fft_bins

    def getGenerator(self, options):
        length = options[c.DATA_OPTIONS][c.OPTIONS_LENGTH]
        target_freqs = options[c.DATA_FREQS]
        while True:
            coordinates = yield
            self.checkLength(len(coordinates), self.getFftLength(length))
            max_value, max_index = self.getMax(
                lambda target_freq: self.getMagnitude(
                    target_freq,
                    self.harmonics,
                    self.interpolation(self.getFreqs(len(coordinates)), coordinates)
                ),
                target_freqs
            )
            # print max_value, sum(coordinates[channel])/len(coordinates[channel])*2+1
            # if sum(coordinates[channel])/len(coordinates[channel])*2+1 < max_value:
            #     max_freqs[max_index] += 1
            yield target_freqs[max_index]
