import numpy as np
import scipy.stats

from training.curve_fitting import SumSkewNormal
from training.itr_calculators import AbstractCalculator

import operator


class ProbValuesHandler(AbstractCalculator.ValuesHandler):
    def getValueAt(self, xs):
        return 1-self.getValueFromCurve(self.fit_curves, xs)

    def getDerivativeValueAt(self, xs):
        return -self.getValueFromCurve(self.fit_curve_derivative, xs)


class ItrCalculatorProb(AbstractCalculator.ItrCalculator):
    def __init__(self, window_length, step, feature_maf_length, proba_maf_length, look_back_length, n_targets):
        AbstractCalculator.ItrCalculator.__init__(self, window_length, step, feature_maf_length, proba_maf_length, look_back_length, n_targets)
        self.prob_curve_fitting = SumSkewNormal.DistrubutionSumCurves()
        self.prob_value_handler = None
        # self.prob_pi = None
        # self.prob_cj = None
        # self.prob_pi_derivative = None
        # self.prob_cj_derivative = None
        self.function_pi_cj = None
        self.derivative_pi_cj = None
        self.class_probas = None
        self.function_cj_pi = None
        self.derivative_cj_pi = None
        self.n_classes = None

    def fitCurves(self, all_predicted_scores, labels, all_thresholds, all_precisions, all_relative_predictions):
        self.setValues(all_predicted_scores, labels)
        self.calculateCurves(all_predicted_scores, labels)

    def calculateCurves(self,  all_predicted_scores, all_labels):
        self.class_probas = np.sum(all_labels, 1)/float(len(all_labels[0]))
        self.prob_curve_fitting.fitCurves(all_predicted_scores, all_labels)
        # functions, derivatives = self.prob_curve_fitting.fitCurves(all_predicted_scores, labels)
        # self.prob_value_handler = ProbValuesHandler(None, functions, derivatives)
        # self.prob_pi, self.prob_pi_derivative = self.prob_curve_fitting.getFitPi()
        # self.prob_cj, self.prob_cj_derivative = self.prob_curve_fitting.getFitCj()
        self.parameters_pi_cj = self.prob_curve_fitting.getParameters()
        self.parameters_cj_pi = self.transposeParameterMatrix(self.parameters_pi_cj)
        self.function_pi_cj, self.derivative_pi_cj = self.prob_curve_fitting.getFitPiGivenCj()
        self.function_cj_pi = np.transpose(self.function_pi_cj)
        self.derivative_cj_pi = np.transpose(self.derivative_pi_cj)
        self.n_classes = len(self.function_pi_cj)

    def transposeParameterMatrix(self, matrix):
        result = [[None for _ in range(len(matrix))] for _ in range(len(matrix))]
        for i, row in enumerate(matrix):
            for j, element in enumerate(row):
                result[j][i] = element
        return result

    def itrFromThresholds(self, thresholds):
        return self.mutualInformation(thresholds)

    def gradient(self, thresholds):
        return [self.mutualInformation(thresholds, d) for d in range(self.n_classes)]

    def mutualInformation(self, ts, derivative_index=-1):
        if derivative_index == -1:
            return self.entropyP(ts, -1) - self.entropyPgivenC(ts, -1)
        else:
            return self.entropyPderivative(ts, derivative_index) - self.entropyPgivenCderivative(ts, derivative_index)

    def entropyP(self, ts, derivative_index):
        return -sum(prob*np.log2(prob) for prob in (self.probPi(ts, i, -1) for i in range(self.n_classes)))
        # sum = 0
        # for i in range(self.n_classes):
        #     prob = self.probPi(ts, i, derivative_index)
        #     sum += -prob*np.log2(prob)
        # # print "entropy", sum
        # return sum

    # def entropyOrDerivative(self, ts, func, derivative_index):
    #     if derivative_index == -1:
    #         return self.entropy(ts, func, derivative_index)
    #     else:
    #         return self.entropyDerivative(ts, func, derivative_index)

    # def entropyP(self, ts, derivative_index):
    #     return self.entropyOrDerivative(ts, self.probPi, derivative_index)

    def entropyPderivative(self, ts, derivative_index):
        return -sum(prob_derivative*((np.log(prob)+1)/np.log(2)) for prob, prob_derivative in ((self.probPi(ts, i, -1), self.probPi(ts, i, derivative_index)) for i in range(self.n_classes)))
        # sum = 0
        # for i in range(self.n_classes):
        #     prob = self.probPi(ts, i, -1)
        #     prob_derivative = self.probPi(ts, i, derivative_index)
        #     sum += -prob_derivative*((np.log(prob) + 1)/np.log(2))
        # # print "entropyDerivative", sum
        # return sum

    def entropyOfPgivenC(self, ts, parameters, derivative_index):
        return -sum(prob*np.log2(prob) for prob in (self.probPiGivenCj(ts, i, parameters, -1) for i in range(self.n_classes)))
        # sum = 0
        # for i in range(self.n_classes):
        #     prob = self.probPiGivenCj(ts, i, parameters, derivative_index)
        #     sum += -prob*np.log2(prob)
        # # print "entropyDerivative", sum
        # return sum

    def entropyOfPgivenCderivative(self, ts, parameters, derivative_index):
        return -sum(prob_derivative*((np.log(prob)+1)/np.log(2)) for prob, prob_derivative in ((self.probPiGivenCj(ts, i, parameters, -1), self.probPiGivenCj(ts, i, parameters, derivative_index)) for i in range(self.n_classes)))
        # sum = 0
        # for i in range(self.n_classes):
        #     prob = self.probPiGivenCj(ts, i, parameters, -1)
        #     prob_derivative = self.probPiGivenCj(ts, i, parameters, derivative_index)
        #     sum += -prob_derivative*((np.log(prob) + 1)/np.log(2))
        # # print "entropyDerivative", sum
        # return sum

    def entropyPgivenCderivative(self, ts, derivative_index):  # TODO: Check minus
        return sum(
            prob_ck_derivative*inner_sum + prob_ck*inner_sum_derivative
            for inner_sum, inner_sum_derivative, prob_ck, prob_ck_derivative in ((
                self.entropyOfPgivenC(ts, self.parameters_cj_pi[j], -1),
                self.entropyOfPgivenCderivative(ts, self.parameters_cj_pi[j], derivative_index),
                self.probCk(ts, j, -1),
                self.probCk(ts, j, derivative_index)
            ) for j in range(self.n_classes))
        )
        # sum = 0
        # for j in range(self.n_classes):
        #     inner_sum = self.entropyOfPgivenC(ts, self.parameters_cj_pi[j], -1)
        #     inner_sum_derivative = self.entropyOfPgivenCderivative(ts, self.parameters_cj_pi[j], derivative_index)
        #     prob_ck = self.probCk(ts, j, -1)
        #     prob_ck_derivative = self.probCk(ts, j, derivative_index)
        #     sum += prob_ck_derivative*inner_sum + prob_ck*inner_sum_derivative
        #     # print "entropyPgivenC", sum
        # return sum

    def entropyPgivenC(self, ts, derivative_index):
        return sum(inner_sum*prob for inner_sum, prob in ((self.entropyOfPgivenC(ts, self.parameters_cj_pi[j], -1), self.probCk(ts, j, -1)) for j in range(self.n_classes)))
        # sum = 0
        # for j in range(self.n_classes):
        #     inner_sum = self.entropyOfPgivenC(ts, self.parameters_cj_pi[j], -1)
        #     sum += inner_sum*self.probCk(ts, j, -1)
        # # print "entropyPgivenC", sum
        # return -sum

    def pdf(self, t, parameters):
        return scipy.stats.skewnorm.pdf(t, *parameters)

    def cdf(self, t, parameters):
        return scipy.stats.skewnorm.cdf(t, *parameters)

    def product(self, iterable):
        return reduce(operator.mul, iterable, 1)

    def probPiGivenCj(self, xs, p, parameters, derivative_index):
        return self.product(
            ((1-self.cdf(x, param) if derivative_index != i else -self.pdf(x, param)) if i == p else
             (self.cdf(x, param) if derivative_index != i else self.pdf(x, param)))
            for i, (param, x) in enumerate(zip(parameters, xs))
        )
        # product = 1.0
        # for i, (param, x) in enumerate(zip(parameters, xs)):
        #     if i == p:
        #         product *= ((1-self.cdf(x, param)) if derivative_index != i else -self.pdf(x, param))
        #     else:
        #         product *= (self.cdf(x, param) if derivative_index != i else self.pdf(x, param))
        #     # print "probPiGivenCj", product
        # return product

    def probPi(self, xs, p, derivative_index):
        return sum(self.probPiGivenCj(xs, p, parameters_cj_pi, derivative_index)*class_proba for j, (parameters_cj_pi, class_proba) in enumerate(zip(self.parameters_cj_pi, self.class_probas)))
        # sum = 0.0
        # for j, (parameters_cj_pi, class_proba) in enumerate(zip(self.parameters_cj_pi, self.class_probas)):
        #     sum += self.probPiGivenCj(xs, p, parameters_cj_pi, derivative_index)*class_proba
        # # print "probPi", sum
        # return sum

    def probCk(self, xs, k, derivative_index):
        return sum(self.probPiGivenCj(xs, i, self.parameters_cj_pi[k], derivative_index)*self.class_probas[k] for i in range(self.n_classes))
        # sum = 0.0
        # for i in range(self.n_classes):
        #     sum += self.probPiGivenCj(xs, i, self.parameters_cj_pi[k], derivative_index)*self.class_probas[k]
        # # print "probCk", sum
        # return sum
