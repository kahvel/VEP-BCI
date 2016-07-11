import numpy as np
from nitime import algorithms

import constants as c
import PsdaRanker
from generators.result import Logic


class AutoregressivePSD(PsdaRanker.PsdaRanker):
    def __init__(self):
        PsdaRanker.PsdaRanker.__init__(self)

    def setup(self, options):
        PsdaRanker.PsdaRanker.setup(self, options)

    def getResults(self, data):
        coefficients, sigma_squared = algorithms.AR_est_YW(data, 100)
        length = self.target_magnitude_handler.max_signal_length
        normalised_frequencies, coefficients_psd = algorithms.AR_psd(coefficients, sigma_squared, length-1)
        self.target_magnitude_handler.max_length_fft_bins = (normalised_frequencies*c.HEADSET_FREQ/(2*np.pi))[1:]
        return PsdaRanker.PsdaRanker.getResults(self, coefficients_psd[1:])


class PsdaFromSignal(PsdaRanker.PsdaRanker):
    def __init__(self):
        PsdaRanker.PsdaRanker.__init__(self)
        self.psda_handler = Logic.PSDA()

    def setup(self, options):
        PsdaRanker.PsdaRanker.setup(self, options)
        self.psda_handler.setup(options)

    def getResults(self, signal):
        amplitude_spectrum = self.psda_handler.calculatePSD(signal)
        return PsdaRanker.PsdaRanker.getResults(self, amplitude_spectrum)


class SNR(Logic.TargetFrequencies, Logic.Harmonics):
    def __init__(self):
        Logic.TargetFrequencies.__init__(self)
        Logic.Harmonics.__init__(self)
        self.autoregressive_psd_handler = AutoregressivePSD()
        self.signal_psda_ranker = PsdaFromSignal()
        self.result = None

    def setup(self, options):
        Logic.TargetFrequencies.setup(self, options)
        Logic.Harmonics.setup(self, options)
        self.autoregressive_psd_handler.setup(options)
        self.signal_psda_ranker.setup(options)

    def updateSNRs(self, result, signal_results, noise_results):
        for harmonic in self.harmonics:
            signal_freq_results = dict(signal_results[harmonic])
            noise_freq_results = dict(noise_results[harmonic])
            for freq in self.frequencies:
                result[harmonic][freq] += signal_freq_results[freq]/noise_freq_results[freq]

    def calculateSNR(self, projected_signal, projected_noise):
        self.result = {harmonic: {freq: 0 for freq in self.frequencies} for harmonic in self.harmonics}
        for signal, noise in zip(projected_signal, projected_noise):
            signal_results = self.signal_psda_ranker.getResults(signal)
            noise_results = self.autoregressive_psd_handler.getResults(noise)
            # print signal_results
            # print noise_results
            self.updateSNRs(self.result, signal_results, noise_results)
        return self.result


class PsdaSnrRanker(Logic.Ranker):
    def __init__(self):
        Logic.Ranker.__init__(self)
        self.projection_onto_reference_signals = Logic.ProjectionOntoReferenceSignals()
        self.projection_onto_principal_components = Logic.ProjectionOntoLastPrincipalComponents()
        self.sum_result_adder = Logic.SumResultAdder()
        self.snr_handler = SNR()

    def setup(self, options):
        Logic.Ranker.setup(self, options)
        self.projection_onto_reference_signals.setup(options)
        self.projection_onto_principal_components.setup(options)
        self.sum_result_adder.setup(options)
        self.snr_handler.setup(options)

    def projectOntoPrincipalComponents(self, signal_coordinates, noise_components):
        self.projection_onto_principal_components.initialiseProjectionMatrix(noise_components)
        projected_signal = self.projection_onto_principal_components.project(np.transpose(signal_coordinates))
        # print projected_signal.shape
        projected_noise = self.projection_onto_principal_components.project(np.transpose(noise_components))
        return projected_signal, projected_noise

    def calculateNoise(self, signal_coordinates):
        return signal_coordinates - self.projection_onto_reference_signals.project(signal_coordinates)

    def getResults(self, signal_coordinates):
        """
        Projection matrix and coefficient PSDA ranker (fft_bins) works only if is_short==False.
        :param signal_coordinates:
        :return:
        """
        signal_coordinates = np.transpose(signal_coordinates)
        noise_components = self.calculateNoise(signal_coordinates)
        projected_signal, projected_noise = self.projectOntoPrincipalComponents(signal_coordinates, noise_components)
        snr = self.snr_handler.calculateSNR(projected_signal, projected_noise)
        final = self.sum_result_adder.addSumAndOrderResult(snr)
        # print final
        # print
        return final
