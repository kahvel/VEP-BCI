import numpy as np
import sklearn.cross_decomposition
from sklearn import preprocessing
from sklearn.decomposition import PCA
from nitime import algorithms

import constants as c
from generators import AbstractGenerator


class ExtractionWithReferenceSignals(AbstractGenerator.AbstractExtracionGenerator):
    def __init__(self):
        """
        The class which Extraction uses to extract features. Extraction receives messages and sends it here.
        This class does all the processing and sends back the extracted feature (correlation with reference signals).
        :return:
        """
        AbstractGenerator.AbstractExtracionGenerator.__init__(self)
        self.reference_signals = None
        self.target_freqs = None

    def setup(self, options):
        AbstractGenerator.AbstractExtracionGenerator.setup(self, options)
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

    def getReferenceSignal(self, target_reference, length):
        if self.short_signal:
            return np.array([target_reference[j][:length] for j in range(len(target_reference))])
        else:
            return np.array(target_reference)

    def getResults(self, coordinates, length, target_freqs):
        return ((freq, self.getCorr(coordinates, self.getReferenceSignal(reference, length).T)) for freq, reference in zip(target_freqs, self.reference_signals))

    def getRanking(self, results):
        return sorted(results, key=lambda x: x[1], reverse=True)

    def getGenerator(self, options):
        max_length = options[c.DATA_OPTIONS][c.OPTIONS_LENGTH]
        generator_count = len(options[c.DATA_SENSORS])
        target_freqs = options[c.DATA_FREQS].values()
        coordinates = [[] for _ in range(generator_count)]
        while True:
            for i in range(generator_count):
                coordinates[i] = yield
            actual_length = len(coordinates[0])
            self.checkLength(actual_length, max_length)
            transposed_coordinates = np.array(coordinates).T
            yield self.getRanking(self.getResults(transposed_coordinates, actual_length, target_freqs))

    def getCorr(self, signal, reference):
        raise NotImplementedError("getCorr not implemented!")


class CcaExtraction(ExtractionWithReferenceSignals):
    def __init__(self):
        ExtractionWithReferenceSignals.__init__(self)
        self.model = None

    def setup(self, options):
        ExtractionWithReferenceSignals.setup(self, options)
        self.model = sklearn.cross_decomposition.CCA(n_components=1)

    def getCorr(self, signal, reference):
        self.model.fit(signal, reference)
        res_x, res_y = self.model.transform(signal, reference)
        corr = np.corrcoef(res_x.T, res_y.T)[0][1]
        return corr


class LrtExtraction(ExtractionWithReferenceSignals):
    def __init__(self):
        ExtractionWithReferenceSignals.__init__(self)

    def setup(self, options):
        """
        Centralise reference signals (along samples).
        AbstractExtractionGenerator sets self.harmonics value from options and self.short_signal to True.
        In addition calls AbstractPythonGenerator setup which sets self.generator value using self.getGenerator and
        sends None to it.
        :param options: Dictionary of options
        :return:
        """
        ExtractionWithReferenceSignals.setup(self, options)
        for i in range(len(self.reference_signals)):
            preprocessing.scale(self.reference_signals[i], axis=1, with_std=False)

    def getCorr(self, signal, reference):
        """
        Replace canonical correlation calculation with LRT.
        Centralises signal.
        :param signal: Multidimensional input signal. Shape: (window length, number of sensors).
        :param reference: Centralised reference signals for one target. Shape: (window length, 2 times the number of harmonics)
        :return: LRT result
        """
        preprocessing.scale(signal, axis=1, with_std=False)  # centralise samples
        X = np.column_stack((signal, reference))
        sigma_hat = np.cov(X, rowvar=False)
        sigma_11 = np.cov(signal, rowvar=False)
        sigma_22 = np.cov(reference, rowvar=False)
        V = np.linalg.det(sigma_hat)/(np.linalg.det(sigma_11)*np.linalg.det(sigma_22))
        p2 = reference.shape[1]
        C = 1-V**(1.0/p2)
        return C


class PsdaSnrExtraction(ExtractionWithReferenceSignals):
    def __init__(self):
        ExtractionWithReferenceSignals.__init__(self)
        self.projection_matrix = None
        self.flat_reference_signals = None

    def setup(self, options):
        ExtractionWithReferenceSignals.setup(self, options)
        self.flat_reference_signals = [signal for sublist in self.reference_signals for signal in sublist]
        self.projection_matrix = self.calculateProjectionMatrix(self.flat_reference_signals)

    def calculateProjectionMatrix(self, At):
        A = np.transpose(At)
        AtA_inverse = np.linalg.inv(np.dot(At, A))
        return np.dot(np.dot(A, AtA_inverse), At)

    def getLastPrincipalComponents(self, data):
        model = PCA()
        model.fit(data)
        print model.components_.shape
        new_axis = []
        variance_explained = 0
        for i, variance_ratio in enumerate(reversed(model.explained_variance_ratio_)):
            variance_explained += variance_ratio
            print variance_explained, model.explained_variance_ratio_
            if variance_explained < 0.1:
                new_axis.append(model.components_[-(i+1)])
            else:
                break
        if len(new_axis) == 0:
            return [model.components_[-1]]
        else:
            return new_axis

    def getResults(self, coordinates, length, target_freqs):
        noise_components = coordinates - np.dot(self.projection_matrix, coordinates)
        new_axis = self.getLastPrincipalComponents(noise_components)
        projected_coordinates = np.dot(new_axis, np.transpose(coordinates))
        for projected in projected_coordinates:
            coefficients, sigma_squared = algorithms.AR_est_YW(projected, 10)
            normalised_frequencies, coefficients_psd = algorithms.AR_psd(coefficients, sigma_squared, max_length)
            print normalised_frequencies*c.HEADSET_FREQ/np.pi, coefficients_psd
            raw_input()