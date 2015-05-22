__author__ = 'Anti'

import numpy as np
import sklearn.cross_decomposition
import constants as c
from generators import Generator


class CcaExtraction(Generator.AbstractExtracionGenerator):
    def __init__(self):
        Generator.AbstractExtracionGenerator.__init__(self)
        self.cca = None
        self.reference_signals = None

    def setup(self, options):
        Generator.AbstractExtracionGenerator.setup(self, options)
        self.cca = sklearn.cross_decomposition.CCA(n_components=1)
        self.reference_signals = self.getReferenceSignals(options[c.DATA_OPTIONS][c.OPTIONS_LENGTH], options[c.DATA_FREQS])

    def getReferenceSignals(self, length, target_freqs):
        reference_signals = []
        t = np.arange(0, length, step=1.0)/c.HEADSET_FREQ
        for freq, harmonics in zip(target_freqs, self.harmonics):
            reference_signals.append([])
            for harmonic in harmonics:
                reference_signals[-1].append(np.sin(np.pi*2*harmonic*freq*t))
                reference_signals[-1].append(np.cos(np.pi*2*harmonic*freq*t))
        return reference_signals

    def getCorr(self, signal, reference):
        self.cca.fit(signal, reference)
        res_x, res_y = self.cca.transform(signal, reference)
        corr = np.corrcoef(res_x.T, res_y.T)[0][1]
        return corr

    def getReferenceSignal(self, target_reference, length):
        if self.short_signal:
            return np.array([target_reference[j][:length] for j in range(len(target_reference))])
        else:
            return np.array(target_reference)

    def getResults(self, coordinates, length, target_freqs):
        return {freq: self.getCorr(coordinates, self.getReferenceSignal(reference, length).T) for freq, reference in zip(target_freqs, self.reference_signals)}

    def getGenerator(self, options):
        max_length = options[c.DATA_OPTIONS][c.OPTIONS_LENGTH]
        generator_count = len(options[c.DATA_SENSORS])
        target_freqs = options[c.DATA_FREQS]
        coordinates = [[] for _ in range(generator_count)]
        while True:
            for i in range(generator_count):
                coordinates[i] = yield
            actual_length = len(coordinates[0])
            self.checkLength(actual_length, max_length)
            transposed_coordinates = np.array(coordinates).T
            yield self.getResults(transposed_coordinates, actual_length, target_freqs)