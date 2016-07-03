import numpy as np
import constants as c


class AbstractPythonGenerator(object):
    def __init__(self):
        self.generator = None

    def setup(self, options):
        self.generator = self.getGenerator(options)
        self.generator.send(None)

    def getGenerator(self, options):
        raise NotImplementedError("getGenerator not implemented!")

    def send(self, message):
        return self.generator.send(message)

    def next(self):
        self.generator.next()


class AbstractMyGenerator(AbstractPythonGenerator):
    def __init__(self):
        AbstractPythonGenerator.__init__(self)

    def setup(self, options):
        self.generator = self.getGenerator(options)
        self.generator.setup(options)


class GeneratorWithReferenceSignals(AbstractPythonGenerator):
    def __init__(self):
        """
        This class is used to provide getReferenceSignals function to SignalProcessing and
        ExtractionWithReferenceSignals through SignalProcessingGenerator and AbstractExtractionGenerator.
        :return:
        """
        AbstractPythonGenerator.__init__(self)
        self.harmonics = None

    def getReferenceSignals(self, length, target_freqs):
        """
        Returns reference signals grouped per target. Each target has number of harmonics times two reference signals,
        that is sine and cosine for each harmonic. Needed in CCA and LRT extraction in ExtractionWithReferenceSignals
        and also in SignalProcessing.
        :param length: Length of the window.
        :param target_freqs: List of target frequencies.
        :return:
        """
        reference_signals = []
        t = np.arange(0, length, step=1.0)/c.HEADSET_FREQ
        self.harmonics = [self.harmonics]*len(target_freqs)
        for freq, harmonics in zip(target_freqs, self.harmonics):
            reference_signals.append([])
            for harmonic in harmonics:
                reference_signals[-1].append(np.sin(np.pi*2*harmonic*freq*t))
                reference_signals[-1].append(np.cos(np.pi*2*harmonic*freq*t))
        return reference_signals


class SignalProcessingGenerator(GeneratorWithReferenceSignals):
    def setup(self, options):
        """
        The function is the same as in AbstractMyGenerator. Previously AbstractMyGenerator was SignalProcessing
        superclass but since we need reference signals in SignalProcessing now this is its superclass.
        :param options:
        :return:
        """
        self.generator = self.getGenerator(options)
        self.generator.setup(options)


class AbstractExtractionGenerator(GeneratorWithReferenceSignals):
    def __init__(self):
        """
        Used in PsdaExtraction and ExtractionWithReferenceSignals. Extraction.Extraction uses these subclasses to
        extract features. It sends here the processed signal and expects to get back the ranked features.
        :return:
        """
        GeneratorWithReferenceSignals.__init__(self)
        self.short_signal = None

    def setup(self, options):
        AbstractPythonGenerator.setup(self, options)
        self.harmonics = self.getHarmonics(options)
        self.short_signal = True

    def getHarmonics(self, options):
        return options[c.DATA_HARMONICS]

    def checkLength(self, signal_length, options_length):
        if self.short_signal and signal_length == options_length:
            self.short_signal = False
