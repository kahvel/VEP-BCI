import numpy as np

from training.curve_fitting import SumSkewNormal
from training.itr_calculators import AbstractCalculator


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
        self.function_pi_cj, self.derivative_pi_cj = self.prob_curve_fitting.getFitPiGivenCj()
        self.function_cj_pi = np.transpose(self.function_pi_cj)
        self.derivative_cj_pi = np.transpose(self.derivative_pi_cj)
        self.n_classes = len(self.function_pi_cj)

    def itrFromThresholds(self, thresholds):
        return self.mutualInformation(thresholds)

    def gradient(self, thresholds):
        return [self.mutualInformation(thresholds, d) for d in range(self.n_classes)]

    def mutualInformation(self, ts, derivative_index=-1):
        return self.entropyP(ts, derivative_index) - self.entropyPgivenC(ts, derivative_index)

    def entropy(self, ts, func, derivative_index):
        sum = 0
        for i in range(self.n_classes):
            prob = func(ts, i, derivative_index)
            sum += -prob*np.log2(prob)
        return sum

    def entropyOrDerivative(self, ts, func, derivative_index):
        if derivative_index == -1:
            return self.entropy(ts, func, derivative_index)
        else:
            return self.entropyDerivative(ts, func, derivative_index)

    def entropyP(self, ts, derivative_index):
        return self.entropyOrDerivative(ts, self.probPi, derivative_index)

    def entropyDerivative(self, ts, func, derivative_index):
        sum = 0
        for i in range(self.n_classes):
            prob = func(ts, i, -1)
            prob_derivative = func(ts, i, derivative_index)
            sum += -prob_derivative*((np.log(prob) + 1)/np.log(2))
        return sum

    def entropyPgivenC(self, ts, derivative_index):
        if derivative_index == -1:
            sum = 0
            for j in range(self.n_classes):
                func = lambda ts, i, d: self.probPiGivenCj(ts, i, self.function_cj_pi[j], self.derivative_cj_pi[j], d)
                inner_sum = self.entropyOrDerivative(ts, func, derivative_index)
                sum += inner_sum*self.probCk(ts, j, derivative_index)
            return sum
        else:
            sum = 0
            for j in range(self.n_classes):
                func = lambda ts, i, d: self.probPiGivenCj(ts, i, self.function_cj_pi[j], self.derivative_cj_pi[j], d)
                inner_sum = self.entropyOrDerivative(ts, func, -1)
                inner_sum_derivative = self.entropyOrDerivative(ts, func, derivative_index)
                prob_ck = self.probCk(ts, j, -1)
                prob_ck_derivative = self.probCk(ts, j, derivative_index)
                sum += prob_ck_derivative*inner_sum + prob_ck*inner_sum_derivative
            return sum

    def probPiGivenCj(self, xs, p, functions, derivatives, derivative_index=-1):
        product = 1.0
        for i, (function, derivative, x) in enumerate(zip(functions, derivatives, xs)):
            if i == p:
                product *= ((1-function(x)) if derivative_index != i else -derivative(x))
            else:
                product *= (function(x) if derivative_index != i else derivative(x))
        return product

    def probPi(self, xs, p, derivative_index):
        sum = 0.0
        for j, (functions_cj_fi, derivatives, class_proba) in enumerate(zip(self.function_cj_pi, self.derivative_cj_pi, self.class_probas)):
            sum += self.probPiGivenCj(xs, p, functions_cj_fi, derivatives, derivative_index)*class_proba
        return sum

    def probCk(self, xs, k, derivative_index):
        sum = 0.0
        for i in range(self.n_classes):
            sum += self.probPiGivenCj(xs, i, self.function_cj_pi[k], self.derivative_cj_pi[k], derivative_index)*self.class_probas[k]
        return sum

