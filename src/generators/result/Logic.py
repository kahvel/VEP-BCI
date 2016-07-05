import numpy as np
import scipy.interpolate

import constants as c


class Logic(object):
    def __init__(self):
        self.max_signal_length = None

    def getMaxSignalLength(self, options):
        return options[c.DATA_OPTIONS][c.OPTIONS_LENGTH]

    def setup(self, options):
        self.max_signal_length = self.getMaxSignalLength(options)


class FftBins(Logic):
    def __init__(self):
        Logic.__init__(self)
        self.max_length_fft_bins = None
        self.max_fft_length = None

    def setup(self, options):
        Logic.setup(self, options)
        self.max_length_fft_bins = self.calculateBins(self.max_signal_length)
        self.max_fft_length = self.getFftLength(self.max_signal_length)

    def getFftLength(self, signal_length):
        return signal_length//2

    def getSignalLength(self, fft_length):
        """
        Given the length of fft-1 (without zero frequency), calculates the length of the original signal.
        Assumes that the original signal length is an even number. If it was odd, the result of this function is one
        less than the actual length.
        :param fft_length:
        :return:
        """
        return fft_length*2

    def getBins(self, fft_length):
        if fft_length < self.max_fft_length:
            return self.calculateBins(self.getSignalLength(fft_length))
        else:
            return self.max_length_fft_bins

    def calculateBins(self, signal_length):
        """
        Calculates the frequency bins of given signal length. Does not include zero frequency.
        :param signal_length:
        :return:
        """
        return np.fft.rfftfreq(signal_length)[1:]*c.HEADSET_FREQ


class InterpolationAndFftBins(FftBins):
    def __init__(self):
        FftBins.__init__(self)
        self.interpolationFunc = None
        self.menu_key_to_scipy_key = {
            c.INTERPOLATE_LINEAR: c.SCIPY_INTERPOLATE_LINEAR,
            c.INTERPOLATE_NEAREST: c.SCIPY_INTERPOLATE_NEAREST,
            c.INTERPOLATE_ZERO: c.SCIPY_INTERPOLATE_ZERO,
            c.INTERPOLATE_CUBIC: c.SCIPY_INTERPOLATE_CUBIC,
            c.INTERPOLATE_SLINEAR: c.SCIPY_INTERPOLATE_SLINEAR,
            c.INTERPOLATE_QUADRATIC: c.SCIPY_INTERPOLATE_QUADRATIC
        }

    def setup(self, options):
        FftBins.setup(self, options)
        self.interpolationFunc = self.getInterpolation(options[c.DATA_OPTIONS])

    def getInterpolation(self, options):
        if options[c.OPTIONS_INTERPOLATE] in self.menu_key_to_scipy_key:
            return lambda x, y: scipy.interpolate.interp1d(x, y, kind=self.menu_key_to_scipy_key[options[c.OPTIONS_INTERPOLATE]])
        elif options[c.OPTIONS_INTERPOLATE] == c.INTERPOLATE_BARYCENTRIC:
            return lambda x, y: scipy.interpolate.BarycentricInterpolator(x, y)
        else:
            raise ValueError("Illegal argument in getInterpolation: " + str(options[c.OPTIONS_INTERPOLATE]))


class TargetFrequencies(Logic):
    def __init__(self):
        Logic.__init__(self)
        self.frequencies_dict = None
        self.frequency_count = None
        self.frequencies = None

    def setup(self, options):
        Logic.setup(self, options)
        self.frequencies_dict = options[c.DATA_FREQS]
        self.frequency_count = len(self.frequencies_dict)
        self.frequencies = self.frequencies_dict.values()


class Harmonics(TargetFrequencies):
    def __init__(self):
        TargetFrequencies.__init__(self)
        self.harmonics = None

    def setup(self, options):
        TargetFrequencies.setup(self, options)
        self.harmonics = options[c.DATA_HARMONICS]


class ReferenceSignals(Harmonics):
    def __init__(self):
        Harmonics.__init__(self)
        self.reference_signals = None

    def setup(self, options):
        Harmonics.setup(self, options)
        self.reference_signals = self.getReferenceSignals(
            self.getMaxSignalLength(options),
            self.frequencies,
            self.getHarmonicsForReferenceSignals()
        )

    def getHarmonicsForReferenceSignals(self):
        return [self.harmonics]*self.frequency_count

    def getReferenceSignals(self, length, frequencies, all_harmonics):
        """
        Returns reference signals grouped per target. Each target has number of harmonics times two reference signals,
        that is sine and cosine for each harmonic.
        :param length:
        :param frequencies:
        :return:
        """
        reference_signals = []
        t = np.arange(0, length, step=1.0)/c.HEADSET_FREQ
        for freq, harmonics in zip(frequencies, all_harmonics):
            reference_signals.append([])
            for harmonic in harmonics:
                reference_signals[-1].append(np.sin(np.pi*2*harmonic*freq*t))
                reference_signals[-1].append(np.cos(np.pi*2*harmonic*freq*t))
        return reference_signals

    def iteraterateSignals(self, length):
        for frequency, signal in zip(self.frequencies, self.reference_signals):
            yield frequency, self.getSignal(signal, length)

    def getSignal(self, target_reference, length):
        if length < self.max_signal_length:
            return np.array([target_reference[j][:length] for j in range(len(target_reference))])
        else:
            return np.array(target_reference)
