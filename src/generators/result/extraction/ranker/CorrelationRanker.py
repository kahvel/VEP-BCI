import sklearn.cross_decomposition
import sklearn.preprocessing
import numpy as np

from generators.result import Logic


class CorrelationRanker(Logic.Ranker):
    def __init__(self):
        Logic.Ranker.__init__(self)
        self.reference_signal_handler = Logic.ReferenceSignals()

    def setup(self, options):
        Logic.Ranker.setup(self, options)
        self.reference_signal_handler.setup(options)

    def getCorr(self, signal, reference):
        raise NotImplementedError("getCorr not implemented!")

    def getResults(self, coordinates):
        return self.getRanking(
            (freq, self.getCorr(np.transpose(coordinates), np.transpose(reference)))
            for freq, reference in self.reference_signal_handler.iteraterateSignals(len(coordinates[0]))
        )


class LrtRanker(CorrelationRanker):
    def __init__(self):
        CorrelationRanker.__init__(self)

    def setup(self, options):
        """
        Centralise reference signals (along samples).
        :param options: Dictionary of options
        :return:
        """
        CorrelationRanker.setup(self, options)
        # for i in range(len(self.reference_signals)):
        #     sklearn.preprocessing.scale(self.reference_signals[i], axis=1, with_std=False)

    def getCorr(self, signal, reference):
        """
        Replace canonical correlation calculation with LRT.
        Centralises signal.
        :param signal: Multidimensional input signal. Shape: (window length, number of sensors).
        :param reference: Centralised reference signals for one target. Shape: (window length, 2 times the number
        of harmonics)
        :return: LRT result
        """
        sklearn.preprocessing.scale(signal, axis=1, with_std=False)  # centralise samples
        X = np.column_stack((signal, reference))  # TODO does it make sense?
        sigma_hat = np.cov(X, rowvar=False)
        sigma_11 = np.cov(signal, rowvar=False)
        sigma_22 = np.cov(reference, rowvar=False)
        V = np.linalg.det(sigma_hat)/(np.linalg.det(sigma_11)*np.linalg.det(sigma_22))
        p2 = reference.shape[1]
        C = 1-V**(1.0/p2)
        return C


class CcaRanker(CorrelationRanker):
    def __init__(self):
        CorrelationRanker.__init__(self)
        self.model = None
        self.sensors_handler = Logic.Sensors()
        self.number_of_components = None

    def calculateNumberOfComponents(self):
        return min(self.sensors_handler.sensor_count, self.reference_signal_handler.reference_signal_count)

    def setup(self, options):
        CorrelationRanker.setup(self, options)
        self.sensors_handler.setup(options)
        self.number_of_components = 1  # self.calculateNumberOfComponents()
        self.model = sklearn.cross_decomposition.CCA(n_components=self.number_of_components)

    def getCorr(self, signal, reference):
        self.model.fit(signal, reference)
        res_x, res_y = self.model.transform(signal, reference)
        corr = np.corrcoef(res_x.T, res_y.T)[0][1]
        return corr

    # def getResults(self, coordinates):  # needs change in FeaturesParser
    #     x_weight_result = {"X"+name: {} for name in self.sensors_handler.sensors}
    #     y_weight_result = {"Y"+str(name): {} for name in self.reference_signal_handler.harmonics}
    #     correlation_result = {"C"+str(name): {} for name in range(self.number_of_components)}
    #     for freq, reference in self.reference_signal_handler.iteraterateSignals(len(coordinates[0])):
    #         self.model.fit(np.transpose(coordinates), np.transpose(reference))
    #         for name, weight in zip(x_weight_result, self.model.x_weights_):
    #             x_weight_result[name][freq] = weight[0]
    #         for name, weight in zip(y_weight_result, self.model.y_weights_):
    #             y_weight_result[name][freq] = weight[0]
    #         res_x, res_y = self.model.transform(np.transpose(coordinates), np.transpose(reference))
    #         correlation = np.corrcoef(res_x.T, res_y.T)
    #         for i, name in enumerate(correlation_result):
    #             correlation_result[name][freq] = correlation[i][(i+1)*2-1]  # TODO is this correct?
    #     x_weight_result = {name: self.getRanking(results.items()) for name, results in x_weight_result.items()}
    #     y_weight_result = {name: self.getRanking(results.items()) for name, results in y_weight_result.items()}
    #     correlation_result = {name: self.getRanking(results.items()) for name, results in correlation_result.items()}
    #     result = {}
    #     result.update(x_weight_result)
    #     result.update(y_weight_result)
    #     result.update(correlation_result)
    #     return result
