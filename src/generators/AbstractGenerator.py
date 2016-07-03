import numpy as np
import constants as c


class AbstractGenerator(object):
    def __init__(self):
        self.generator = None

    def setup(self, options):
        self.generator = self.getGenerator(options)

    def getGenerator(self, options):
        raise NotImplementedError("getGenerator not implemented!")

    def send(self, message):
        return self.generator.send(message)

    def next(self):
        self.generator.next()


class AbstractPythonGenerator(AbstractGenerator):
    def setup(self, options):
        AbstractGenerator.setup(self, options)
        self.generator.send(None)


class AbstractMyGenerator(AbstractGenerator):
    def setup(self, options):
        AbstractGenerator.setup(self, options)
        self.generator.setup(options)


class AbstractExtracionGenerator(AbstractPythonGenerator):
    def __init__(self):
        AbstractPythonGenerator.__init__(self)
        self.harmonics = None
        self.short_signal = None
        self.reference_signals = None
        self.target_freqs = None

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

    def setup(self, options):
        AbstractPythonGenerator.setup(self, options)
        self.target_freqs = options[c.DATA_FREQS]
        self.harmonics = self.getHarmonics(options)
        self.reference_signals = self.getReferenceSignals(
            options[c.DATA_OPTIONS][c.OPTIONS_LENGTH],
            self.target_freqs.values(),
            self.getHarmonicsForReferenceSignals(options)
        )
        self.short_signal = True

    def getHarmonicsForReferenceSignals(self, options):
        return [options[c.DATA_HARMONICS]]*len(options[c.DATA_FREQS])

    def getHarmonics(self, options):
        return options[c.DATA_HARMONICS]

    def checkLength(self, signal_length, options_length):
        if self.short_signal and signal_length == options_length:
            self.short_signal = False
