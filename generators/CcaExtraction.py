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
        t = np.arange(0, length)  # TODO???
        for freq in target_freqs:
            reference_signals.append([])
            for harmonic in range(1, self.harmonics+1):
                reference_signals[-1].append(np.sin(np.pi*2*harmonic*freq/c.HEADSET_FREQ*t))
                reference_signals[-1].append(np.cos(np.pi*2*harmonic*freq/c.HEADSET_FREQ*t))
            # reference_signals[-1] = np.array(reference_signals[-1]).T
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

    def getGenerator(self, options):
        length = options[c.DATA_OPTIONS][c.OPTIONS_LENGTH]
        target_freqs = options[c.DATA_FREQS]
        generator_count = len(options[c.DATA_SENSORS])
        coordinates = [None for _ in range(generator_count)]
        while True:
            for i in range(generator_count):
                coordinates[i] = yield
            self.checkLength(len(coordinates[0]), length)
            max_value, max_index = self.getMax(
                lambda target_reference: self.getCorr(
                    np.array(coordinates).T,
                    self.getReferenceSignal(target_reference, len(coordinates[0])).T
                ),
                self.reference_signals
            )
            # print maximum, 0.2
            # if maximum > 0.2:
            #     yield target_freqs[max_index]
            yield target_freqs[max_index]
