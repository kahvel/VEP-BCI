import constants as c

import numpy as np


class Ranker(object):
    def __init__(self):
        pass

    def getRanking(self, results):
        return sorted(results, key=lambda x: x[1], reverse=True)

    def getResults(self, coordinates, length, target_freqs, is_short):
        raise NotImplementedError("getResults not implemented!")

    def setup(self, options):
        raise NotImplementedError("setup not implemented!")


class RankerWithHarmonics(Ranker):
    def __init__(self):
        Ranker.__init__(self)
        self.harmonics = None

    def setup(self, options):
        self.harmonics = self.getHarmonics(options)

    def getHarmonics(self, options):
        return options[c.DATA_HARMONICS]


class RankerWithReferenceSignals(RankerWithHarmonics):
    def __init__(self):
        """
        All rankers with reference signals are not rankers with harmonics, did not know how to fix hierarchy.
        :return:
        """
        Ranker.__init__(self)
        self.reference_signals = None
        self.target_freqs = None

    def setup(self, options):
        RankerWithHarmonics.setup(self, options)
        self.target_freqs = options[c.DATA_FREQS]
        self.reference_signals = self.getReferenceSignals(
            options[c.DATA_OPTIONS][c.OPTIONS_LENGTH],
            self.target_freqs.values(),
            self.getHarmonicsForReferenceSignals(options)
        )

    def getHarmonicsForReferenceSignals(self, options):
        return [options[c.DATA_HARMONICS]]*len(options[c.DATA_FREQS])

    def getReferenceSignals(self, length, target_freqs, all_harmonics):
        """
        Returns reference signals grouped per target. Each target has number of harmonics times two reference signals,
        that is sine and cosine for each harmonic.
        :param length:
        :param target_freqs:
        :return:
        """
        reference_signals = []
        t = np.arange(0, length, step=1.0)/c.HEADSET_FREQ
        for freq, harmonics in zip(target_freqs, all_harmonics):
            reference_signals.append([])
            for harmonic in harmonics:
                reference_signals[-1].append(np.sin(np.pi*2*harmonic*freq*t))
                reference_signals[-1].append(np.cos(np.pi*2*harmonic*freq*t))
        return reference_signals
