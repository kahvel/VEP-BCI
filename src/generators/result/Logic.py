import numpy as np
import scipy.interpolate

import constants as c


class FftBins(object):
    def __init__(self):
        self.fft_bins = None

    def setup(self, options):
        self.fft_bins = self.calculateBins(options[c.DATA_OPTIONS][c.OPTIONS_LENGTH])

    def getSignalLength(self, fft_length):
        """
        Given the length of fft-1 (without zero frequency), calculates the length of the original signal.
        Assumes that the original signal length is an even number. If it was odd, the result of this function is one
        less than the actual length.
        :param fft_length:
        :return:
        """
        return fft_length*2

    def getBins(self, fft_length, is_short):
        if is_short:
            return self.calculateBins(self.getSignalLength(fft_length))
        else:
            return self.fft_bins

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
