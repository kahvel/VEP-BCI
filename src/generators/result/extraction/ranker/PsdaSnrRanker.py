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
        self.psda_ranker = PsdRanker.PsdRanker()

    def setup(self, options):
        Ranker.RankerWithReferenceSignals.setup(self, options)
        self.flat_reference_signals = [signal for sublist in self.reference_signals for signal in sublist]
        self.projection_matrix = self.calculateProjectionMatrix(self.flat_reference_signals)
        self.psda_ranker.setup(options)

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

    def getResults(self, coordinates, length, target_freqs, is_short):
        signal_coordinates = np.transpose(coordinates["Signal"])
        signal_psd = coordinates["PSDA"]
        noise_components = signal_coordinates - np.dot(self.projection_matrix, signal_coordinates)
        new_axis = self.getLastPrincipalComponents(noise_components)
        projected_coordinates = np.dot(new_axis, np.transpose(signal_coordinates))
        for projected in projected_coordinates:
            coefficients, sigma_squared = algorithms.AR_est_YW(projected, 10)
            normalised_frequencies, coefficients_psd = algorithms.AR_psd(coefficients, sigma_squared, length)
            print normalised_frequencies*c.HEADSET_FREQ/np.pi, coefficients_psd
            raw_input()
