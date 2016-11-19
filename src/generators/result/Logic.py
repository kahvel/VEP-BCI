import numpy as np
import scipy.interpolate
from sklearn.decomposition import PCA

import constants as c


class Logic(object):
    def setup(self, options):
        raise NotImplementedError("setup not implemented!")


class SignalLength(Logic):
    def __init__(self):
        self.max_signal_length = None

    def getMaxSignalLength(self, options):
        return options[c.DATA_OPTIONS][c.OPTIONS_LENGTH]

    def setup(self, options):
        self.max_signal_length = self.getMaxSignalLength(options)


class FftBins(SignalLength):
    def __init__(self):
        SignalLength.__init__(self)
        self.max_length_fft_bins = None
        self.max_fft_length = None

    def setup(self, options):
        SignalLength.setup(self, options)
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


class Interpolation(Logic):
    def __init__(self):
        Logic.__init__(self)
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
        self.frequencies_dict = options[c.DATA_FREQS]
        self.frequency_count = len(self.frequencies_dict)
        self.frequencies = sorted(self.frequencies_dict.values())


class Harmonics(Logic):
    def __init__(self):
        Logic.__init__(self)
        self.harmonics = None

    def setup(self, options):
        self.harmonics = options[c.DATA_HARMONICS]


class ReferenceSignals(Harmonics, TargetFrequencies, SignalLength):
    def __init__(self):
        Harmonics.__init__(self)
        TargetFrequencies.__init__(self)
        SignalLength.__init__(self)
        self.reference_signals = None

    def setup(self, options):
        Harmonics.setup(self, options)
        TargetFrequencies.setup(self, options)
        SignalLength.setup(self, options)
        self.reference_signals = self.getReferenceSignals(
            self.max_signal_length,
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


class Projection(Logic):
    def __init__(self):
        Logic.__init__(self)
        self.projection_matrix = None

    def setup(self, options):
        pass

    def calculateProjectionMatrix(self, matrix):
        raise NotImplementedError("calculateProjectionMatrix not implemented!")

    def initialiseProjectionMatrix(self, matrix):
        self.projection_matrix = self.calculateProjectionMatrix(matrix)

    def project(self, coordinates):
        return np.dot(self.projection_matrix, coordinates)


class ProjectionOntoReferenceSignals(ReferenceSignals, Projection):
    def __init__(self):
        ReferenceSignals.__init__(self)
        Projection.__init__(self)

    def setup(self, options):
        ReferenceSignals.setup(self, options)
        Projection.setup(self, options)
        flat_reference_signals = [signal for sublist in self.reference_signals for signal in sublist]
        self.initialiseProjectionMatrix(flat_reference_signals)

    def calculateProjectionMatrix(self, At):
        A = np.transpose(At)
        AtA_inverse = np.linalg.inv(np.dot(At, A))
        return np.dot(np.dot(A, AtA_inverse), At)


class ProjectionOntoLastPrincipalComponents(Projection):
    def __init__(self):
        Projection.__init__(self)

    def setup(self, options):
        Projection.setup(self, options)

    def getLastPrincipalComponents(self, model, threshold):
        new_axis = []
        variance_explained = 0
        for i, (variance_ratio, variance) in enumerate(zip(reversed(model.explained_variance_ratio_), reversed(model.explained_variance_))):
            variance_explained += variance_ratio
            if variance_explained < threshold:
                new_axis.append(self.eigenvectorOverVarianceAsAxis(model.components_[-(i+1)], variance))
            else:
                break
        return new_axis

    def eigenvectorAsAxis(self, component, variance):
        """
        This was used in the article with autoregression.
        """
        return component

    def eigenvectorOverVarianceAsAxis(self, component, variance):
        """
        This was used in Bremen BCI article
        http://iat.uni-bremen.de/fastmedia/98/Paper_P2.pdf
        """
        return component/np.sqrt(variance)


    def addComponentIfEmpty(self, new_axis, model):
        if len(new_axis) == 0:
            print "Added only one component that explains " + str(model.explained_variance_ratio_[-1]) + "% of variance."
            return [model.components_[-1]]
        else:
            return new_axis

    def calculateProjectionMatrix(self, data):
        model = PCA()
        model.fit(data)
        new_axis = self.getLastPrincipalComponents(model, 0.1)
        return self.addComponentIfEmpty(new_axis, model)


class TargetMagnitude(Harmonics, TargetFrequencies, Interpolation, FftBins):
    def __init__(self):
        Harmonics.__init__(self)
        TargetFrequencies.__init__(self)
        Interpolation.__init__(self)
        FftBins.__init__(self)

    def setup(self, options):
        Harmonics.setup(self, options)
        TargetFrequencies.setup(self, options)
        Interpolation.setup(self, options)
        FftBins.setup(self, options)

    def getMagnitude(self, freq, harmonic, interpolation):
        return float(interpolation(freq*harmonic))

    def getMagnitudesPerFrequency(self, harmonic, fft):
        frequency_bins = self.getBins(len(fft))
        interpolationFunc = self.interpolationFunc(frequency_bins, fft)
        return {freq: self.getMagnitude(freq, harmonic, interpolationFunc) for freq in self.frequencies}

    def getMagnitudesPerHarmonic(self, fft):
        return {harmonic: self.getMagnitudesPerFrequency(harmonic, fft) for harmonic in self.harmonics}


class Ranker(Logic):
    def getRanking(self, results):
        return sorted(results, key=lambda x: x[1], reverse=True)

    def getResults(self, coordinates):
        raise NotImplementedError("getResults not implemented!")

    def setup(self, options):
        pass


class SumResultAdder(Ranker, Harmonics, TargetFrequencies):
    def __init__(self):
        Ranker.__init__(self)
        Harmonics.__init__(self)
        TargetFrequencies.__init__(self)

    def setup(self, options):
        Ranker.setup(self, options)
        Harmonics.setup(self, options)
        TargetFrequencies.setup(self, options)

    def getSumResults(self, result):
        return {freq: sum(result[harmonic][freq] for harmonic in self.harmonics) for freq in self.frequencies}

    def orderByResult(self, result):
        return {harmonic: self.getRanking(result[harmonic].items()) for harmonic in self.harmonics+[c.RESULT_SUM]}

    def addSumAndOrderResult(self, result):
        result[c.RESULT_SUM] = self.getSumResults(result)
        return self.orderByResult(result)


class PSDA(Logic):
    def __init__(self):
        Logic.__init__(self)

    def setup(self, options):
        pass

    def calculatePSD(self, signal):
        return (np.abs(np.fft.rfft(signal))**2)[1:]
