import numpy as np
from sklearn.decomposition import PCA
from nitime import algorithms

import constants as c
import Ranker
import PsdRanker


class PsdaSnrRanker(Ranker.RankerWithReferenceSignals):
    def __init__(self):
        Ranker.RankerWithReferenceSignals.__init__(self)
        self.projection_matrix = None
        self.flat_reference_signals = None
        self.signal_psda_ranker = PsdRanker.PsdRanker()
        self.coefficient_psda_ranker = PsdRanker.PsdRanker()

    def setup(self, options):
        Ranker.RankerWithReferenceSignals.setup(self, options)
        self.flat_reference_signals = [signal for sublist in self.reference_signals for signal in sublist]
        self.projection_matrix = self.calculateProjectionMatrix(self.flat_reference_signals)
        self.signal_psda_ranker.setup(options)
        self.coefficient_psda_ranker.setup(options)

    def calculateProjectionMatrix(self, At):
        A = np.transpose(At)
        AtA_inverse = np.linalg.inv(np.dot(At, A))
        return np.dot(np.dot(A, AtA_inverse), At)

    def getLastPrincipalComponents(self, data):
        model = PCA()
        model.fit(data)
        new_axis = []
        variance_explained = 0
        for i, variance_ratio in enumerate(reversed(model.explained_variance_ratio_)):
            variance_explained += variance_ratio
            if variance_explained < 0.1:
                new_axis.append(model.components_[-(i+1)])
            else:
                break
        if len(new_axis) == 0:
            return [model.components_[-1]]
        else:
            return new_axis

    def getResults(self, signal_coordinates, length, target_freqs, is_short):
        """
        Projection matrix and coefficient PSDA ranker (fft_bins) works only if is_short==False.
        :param coordinates:
        :param length:
        :param target_freqs:
        :param is_short:
        :return:
        """
        noise_components = signal_coordinates - np.dot(self.projection_matrix, signal_coordinates)
        new_axis = self.getLastPrincipalComponents(noise_components)
        projected_signal = np.dot(new_axis, np.transpose(signal_coordinates))
        projected_noise = np.dot(new_axis, np.transpose(noise_components))
        print projected_signal.shape
        for signal, noise in zip(projected_signal, projected_noise):
            amplitude_spectrum = (np.abs(np.fft.rfft(signal))**2)[1:]
            signal_results = self.signal_psda_ranker.getResults(amplitude_spectrum, length, target_freqs, is_short)
            coefficients, sigma_squared = algorithms.AR_est_YW(noise, 10)
            normalised_frequencies, coefficients_psd = algorithms.AR_psd(coefficients, sigma_squared, length-1)
            self.coefficient_psda_ranker.fft_bins = (normalised_frequencies*c.HEADSET_FREQ/(2*np.pi))[1:]
            noise_results = self.coefficient_psda_ranker.getResults(coefficients_psd[1:], length, target_freqs, is_short)
            print signal_results
            print noise_results
