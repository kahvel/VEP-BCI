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
        self.prob_pi_given_cj = None
        self.prob_pi_given_cj_derivative = None
        self.class_probas = None

    def calculateCurves(self,  all_predicted_scores, all_labels):
        self.class_probas = np.sum(all_labels, 1)/float(len(all_labels[0]))
        self.prob_curve_fitting.fitCurves(all_predicted_scores, all_labels)
        # functions, derivatives = self.prob_curve_fitting.fitCurves(all_predicted_scores, labels)
        # self.prob_value_handler = ProbValuesHandler(None, functions, derivatives)
        # self.prob_pi, self.prob_pi_derivative = self.prob_curve_fitting.getFitPi()
        # self.prob_cj, self.prob_cj_derivative = self.prob_curve_fitting.getFitCj()
        self.prob_pi_given_cj, self.prob_pi_given_cj_derivative = self.prob_curve_fitting.getFitPiGivenCj()
        self.prob_cj_given_pi = np.transpose(self.prob_pi_given_cj)
        self.prob_cj_given_pi_derivative = np.transpose(self.prob_pi_given_cj_derivative)

    def itrFromThresholds(self, thresholds):
        return sum(thresholds)/100000

    def gradient(self, thresholds):
        return thresholds

    def entropyP(self, ts):
        return -sum(prob_pi(ts)*np.log2(prob_pi) for prob_pi in self.prob_pi)

    def entropyPgivenC(self, ts):
        return

    def probPi(self, xs, p, derivative_index):
        sum = 0.0
        for j, (functions_cj_fi, derivatives, class_proba) in enumerate(zip(self.functions, self.derivatives, self.class_probas)):
            product = 1.0
            for i, (function_cj_fi, derivative, x) in enumerate(zip(functions_cj_fi, derivatives, xs)):
                if i == p:
                    product *= ((1-function_cj_fi(x)) if derivative_index != i else -derivative(x))
                else:
                    product *= (function_cj_fi(x) if derivative_index != i else derivative(x))
            sum += product*class_proba
        return sum

    def probCk(self, xs, k, derivative_index):
        sum = 0.0
        for i in range(len(self.functions)):
            product = 1.0
            for j, (function_same_c_different_f, derivative, x) in enumerate(zip(self.functions, self.derivatives, xs)):
                if i == j:
                    product *= ((1-function_same_c_different_f(x)) if derivative_index != j else -derivative(x))
                else:
                    product *= (function_same_c_different_f(x) if derivative_index != j else derivative(x))
            sum += product*self.class_probas[k]
        return sum