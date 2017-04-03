import numpy as np

from generators.result import Logic
from generators.result.extraction.ranker import Cwt


class WaveletRanker(Logic.Ranker):
    def __init__(self):
        Logic.Ranker.__init__(self)
        self.harmonics = Logic.Harmonics()
        self.frequencies = Logic.TargetFrequencies()
        self.interpolation = Logic.Interpolation()

    def setup(self, options):
        Logic.Ranker.setup(self, options)
        self.harmonics.setup(options)
        self.frequencies.setup(options)
        self.interpolation.setup(options)

    def getResults(self, signal):
        transform = Cwt.Morlet(signal)
        frequencies = transform.scales * transform.fourierwl
        squared = np.abs(transform.cwt)**2
        means = np.mean(squared, axis=1)
        return self.getMagnitudesPerHarmonic(frequencies, means)

    def getMagnitude(self, freq, harmonic, interpolation):
        return float(interpolation(freq*harmonic))

    def getMagnitudesPerFrequency(self, harmonic, frequencies, wcv):
        interpolationFunc = self.interpolation.interpolationFunc(frequencies, wcv)
        return {freq: self.getMagnitude(freq, harmonic, interpolationFunc) for freq in self.frequencies.frequencies}

    def getMagnitudesPerHarmonic(self, frequencies, wcv):
        return {harmonic: self.getMagnitudesPerFrequency(harmonic, frequencies, wcv) for harmonic in self.harmonics.harmonics}
