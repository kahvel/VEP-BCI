import Ranker
import constants as c
from generators.result import Logic


class PsdRanker(Ranker.RankerWithHarmonics):
    def __init__(self):
        Ranker.RankerWithHarmonics.__init__(self)
        self.frequency_handler = Logic.InterpolationAndFftBins()

    def setup(self, options):
        Ranker.RankerWithHarmonics.setup(self, options)
        self.frequency_handler.setup(options)

    def getMagnitude(self, freq, harmonic, interpolation):
        return float(interpolation(freq*harmonic))

    # def getSNR(self, freq, harmonic_count, interpolation):
    #     result = 0
    #     for harmonic in range(harmonic_count):
    #         harmonic_freq = freq*(harmonic+1)
    #         result += interpolation(harmonic_freq)*2/(interpolation(harmonic_freq-1)+interpolation(harmonic_freq+1))
    #     return result

    def getListOfMagnitudes(self, target_freqs, harmonic, interpolation_func):
        return {freq: self.getMagnitude(freq, harmonic, interpolation_func) for freq in target_freqs}

    def getResults(self, fft, target_freqs):
        frequency_bins = self.frequency_handler.getBins(len(fft))
        interpolation_func = self.frequency_handler.interpolationFunc(frequency_bins, fft)
        result = {harmonic: self.getListOfMagnitudes(target_freqs, harmonic, interpolation_func) for harmonic in self.harmonics}
        result[c.RESULT_SUM] = {freq: sum(result[harmonic][freq] for harmonic in self.harmonics) for freq in target_freqs}
        return {harmonic: self.getRanking(result[harmonic].items()) for harmonic in self.harmonics+[c.RESULT_SUM]}
