import numpy as np
import scipy.interpolate

import constants as c
from generators import AbstractGenerator


class PsdaExtraction(AbstractGenerator.AbstractExtractionGenerator):
    def __init__(self):
        AbstractGenerator.AbstractExtractionGenerator.__init__(self)
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
        AbstractGenerator.AbstractExtractionGenerator.setup(self, options)
        self.interpolation = self.getInterpolation(options[c.DATA_OPTIONS])
        self.fft_bins = np.fft.rfftfreq(options[c.DATA_OPTIONS][c.OPTIONS_LENGTH])[1:]*c.HEADSET_FREQ

    def getInterpolation(self, options):
        if options[c.OPTIONS_INTERPOLATE] in self.menu_key_to_scipy_key:
            return lambda x, y: scipy.interpolate.interp1d(x, y, kind=self.menu_key_to_scipy_key[options[c.OPTIONS_INTERPOLATE]])
        elif options[c.OPTIONS_INTERPOLATE] == c.INTERPOLATE_BARYCENTRIC:
            return lambda x, y: scipy.interpolate.BarycentricInterpolator(x, y)
        else:
            raise ValueError("Illegal argument in getInterpolation: " + str(options[c.OPTIONS_INTERPOLATE]))

    def getMagnitude(self, freq, harmonic, interpolation):
        return float(interpolation(freq*harmonic))

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

    def getListOfMagnitudes(self, target_freqs, harmonic, interpolation_func):
        return {freq: self.getMagnitude(freq, harmonic, interpolation_func) for freq in target_freqs}

    def getResults(self, target_freqs, coordinates):
        interpolation_func = self.interpolation(self.getFreqs(len(coordinates)), coordinates)
        result = {harmonic: self.getListOfMagnitudes(target_freqs, harmonic, interpolation_func) for harmonic in self.harmonics}
        result[c.RESULT_SUM] = {freq: sum(result[harmonic][freq] for harmonic in self.harmonics) for freq in target_freqs}
        return {harmonic: self.getRanking(result[harmonic].items()) for harmonic in self.harmonics+[c.RESULT_SUM]}

    def getRanking(self, results):
        return sorted(results, key=lambda x: x[1], reverse=True)

    def getGenerator(self, options):
        max_length = options[c.DATA_OPTIONS][c.OPTIONS_LENGTH]
        target_freqs = options[c.DATA_FREQS].values()
        while True:
            coordinates = yield
            actual_length = len(coordinates)
            self.checkLength(actual_length, self.getFftLength(max_length))
            yield self.getResults(target_freqs, coordinates)
