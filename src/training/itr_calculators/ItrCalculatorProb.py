import numpy as np
import scipy.stats
from rpy2.robjects.packages import importr

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
        self.sn_r_library = importr("sn")

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
        # pdfs_pi_cj = [[self.pdf(t, param) for param in parameters] for (t, parameters) in zip(thresholds, self.parameters_pi_cj)]
        cdfs_pi_cj = [[self.cdf(t, param) for param in parameters] for (t, parameters) in zip(thresholds, self.parameters_pi_cj)]
        # pdfs_cj_pi = np.transpose(pdfs_pi_cj)
        cdfs_cj_pi = np.transpose(cdfs_pi_cj)
        prob_pi_given_cj = [
            [
                self.product(
                    ((1-cdf) if helper == i else (cdf))
                    for i, cdf in enumerate(cdfs)
                ) for j, cdfs in enumerate(cdfs_cj_pi)
            ] for helper in range(self.n_classes)
        ]
        # prob_pi_given_cj_derivative = [
        #     [
        #         [
        #             self.product(
        #                 (((-pdf) if i == d_i else (1-cdf)) if h == i else (pdf if i == d_i else cdf))
        #                 for i, (pdf, cdf) in enumerate(zip(pdfs, cdfs))
        #             ) for pdfs, cdfs in zip(pdfs_cj_pi, cdfs_cj_pi)
        #         ] for h in range(self.n_classes)
        #     ] for d_i in range(self.n_classes)
        # ]
        prob_pi = [
            sum(pi_given_cj*class_proba for j, (pi_given_cj, class_proba) in enumerate(zip(prob_pi_given_cj[i], self.class_probas)))
            for i in range(self.n_classes)
        ]
        R = sum(prob_pi)
        # prob_pi_derivative = [
        #     [
        #         sum(pi_given_cj*class_proba for j, (pi_given_cj, class_proba) in enumerate(zip(prob_pi_given_cj_derivative[d_i][i], self.class_probas)))
        #         for i in range(self.n_classes)
        #     ] for d_i in range(self.n_classes)
        # ]
        prob_ck = [
            (self.class_probas[k]*sum(prob_pi_given_cj[i][k] for i in range(self.n_classes)))
            for k in range(self.n_classes)
        ]
        # prob_ck_derivative = [
        #     [
        #         self.class_probas[k]*sum(prob_pi_given_cj_derivative[d_i][i][k] for i in range(self.n_classes))
        #         for k in range(self.n_classes)
        #     ] for d_i in range(self.n_classes)
        # ]
        entropy_p = -sum(prob*np.log2(prob) for prob in prob_pi)
        # entropy_p_derivative = [
        #     -sum(prob_derivative*((np.log(prob)+1)/np.log(2))
        #          for prob, prob_derivative in zip(prob_pi, prob_pi_derivative[d_i]))
        #     for d_i in range(self.n_classes)
        # ]
        entropy_of_p_given_c = [
            -sum(prob_pi_given_cj[i][k]*np.log2(prob_pi_given_cj[i][k]) for i in range(self.n_classes))
            for k in range(self.n_classes)
        ]
        # entropy_of_p_given_c_derivative = [
        #     [
        #         -sum(prob_pi_given_cj_derivative[d_i][i][k]*((np.log(prob_pi_given_cj[i][k])+1)/np.log(2)) for i in range(self.n_classes))
        #         for k in range(self.n_classes)
        #     ] for d_i in range(self.n_classes)
        # ]
        entropy_p_given_c = sum(entropy_of_p_given_c[j]*prob_ck[j] for j in range(self.n_classes))
        # entropy_p_given_c_derivative = [
        #     sum(
        #         prob_ck_derivative[d_i][j]*entropy_of_p_given_c[j] + prob_ck[j]*entropy_of_p_given_c_derivative[d_i][j]
        #         for j in range(self.n_classes)
        #     ) for d_i in range(self.n_classes)
        # ]
        return (entropy_p - entropy_p_given_c)/R
        # return self.mutualInformation(thresholds)

    def probPiGivenCj(self, cdfs_cj_pi):
        return [
            [
                self.product(
                    ((1-cdf) if helper == i else (cdf))
                    for i, cdf in enumerate(cdfs)
                ) for j, cdfs in enumerate(cdfs_cj_pi)
            ] for helper in range(self.n_classes)
        ]

    def probPiGivnCjDerivative(self, pdfs_cj_pi, cdfs_cj_pi):
        return [
            [
                [
                    self.product(
                        (((-pdf) if i == d_i else (1-cdf)) if h == i else (pdf if i == d_i else cdf))
                        for i, (pdf, cdf) in enumerate(zip(pdfs, cdfs))
                    ) for pdfs, cdfs in zip(pdfs_cj_pi, cdfs_cj_pi)
                ] for h in range(self.n_classes)
            ] for d_i in range(self.n_classes)
        ]

    def probPi(self, prob_pi_given_cj):
        return [
            sum(pi_given_cj*class_proba for j, (pi_given_cj, class_proba) in enumerate(zip(prob_pi_given_cj[i], self.class_probas)))
            for i in range(self.n_classes)
        ]

    def probPiDerivative(self, prob_pi_given_cj_derivative):
        return [
            [
                sum(pi_given_cj*class_proba for j, (pi_given_cj, class_proba) in enumerate(zip(prob_pi_given_cj_derivative[d_i][i], self.class_probas)))
                for i in range(self.n_classes)
            ] for d_i in range(self.n_classes)
        ]

    def probCk(self, prob_pi_given_cj):
        return [
            (self.class_probas[k]*sum(prob_pi_given_cj[i][k] for i in range(self.n_classes)))
            for k in range(self.n_classes)
        ]

    def probCkDerivative(self, prob_pi_given_cj_derivative):
         return [
            [
                self.class_probas[k]*sum(prob_pi_given_cj_derivative[d_i][i][k] for i in range(self.n_classes))
                for k in range(self.n_classes)
            ] for d_i in range(self.n_classes)
        ]

    def entropyP(self, prob_pi):
        return -sum(prob*np.log2(prob) for prob in prob_pi)

    def entropyPderivative(self, prob_pi, prob_pi_derivative):
        return [
            -sum(prob_derivative*((np.log(prob)+1)/np.log(2))
                 for prob, prob_derivative in zip(prob_pi, prob_pi_derivative[d_i]))
            for d_i in range(self.n_classes)
        ]

    def entropyOfPgivenC(self, prob_pi_given_cj):
        return [
            -sum(prob_pi_given_cj[i][k]*np.log2(prob_pi_given_cj[i][k]) for i in range(self.n_classes))
            for k in range(self.n_classes)
        ]

    def entropyOfPgivenCderivative(self, prob_pi_given_cj, prob_pi_given_cj_derivative):
        return [
            [
                -sum(prob_pi_given_cj_derivative[d_i][i][k]*((np.log(prob_pi_given_cj[i][k])+1)/np.log(2)) for i in range(self.n_classes))
                for k in range(self.n_classes)
            ] for d_i in range(self.n_classes)
        ]

    def entropyPgivenC(self, prob_ck, entropy_of_p_given_c):
        return sum(entropy_of_p_given_c[j]*prob_ck[j] for j in range(self.n_classes))

    def entropyPgivenCderivative(self, prob_ck_derivative, entropy_of_p_given_c, prob_ck, entropy_of_p_given_c_derivative):
        return [
            sum(
                prob_ck_derivative[d_i][j]*entropy_of_p_given_c[j] + prob_ck[j]*entropy_of_p_given_c_derivative[d_i][j]
                for j in range(self.n_classes)
            ) for d_i in range(self.n_classes)
        ]

    def mutualInformation(self, entropy_p_derivative, entropy_p_given_c_derivative):
        return [entropy_p_derivative[d_i] - entropy_p_given_c_derivative[d_i] for d_i in range(self.n_classes)]

    def allPdfs(self, thresholds):
        return [[self.pdf(t, param) for param in parameters] for (t, parameters) in zip(thresholds, self.parameters_pi_cj)]

    def allCdfs(self, thresholds):
        return [[self.cdf(t, param) for param in parameters] for (t, parameters) in zip(thresholds, self.parameters_pi_cj)]

    def gradient(self, thresholds):
        pdfs_pi_cj = self.allPdfs(thresholds)
        cdfs_pi_cj = self.allCdfs(thresholds)
        pdfs_cj_pi = np.transpose(pdfs_pi_cj)
        cdfs_cj_pi = np.transpose(cdfs_pi_cj)
        prob_pi_given_cj = self.probPiGivenCj(cdfs_cj_pi)
        prob_pi_given_cj_derivative = self.probPiGivnCjDerivative(pdfs_cj_pi, cdfs_cj_pi)
        prob_pi = self.probPi(prob_pi_given_cj)
        prob_pi_derivative = self.probPiDerivative(prob_pi_given_cj_derivative)
        prob_ck = self.probCk(prob_pi_given_cj)
        prob_ck_derivative = self.probCkDerivative(prob_pi_given_cj_derivative)
        # entropy_p = self.entropyP(prob_pi)
        entropy_p_derivative = self.entropyPderivative(prob_pi, prob_pi_derivative)
        entropy_of_p_given_c = self.entropyOfPgivenC(prob_pi_given_cj)
        entropy_of_p_given_c_derivative = self.entropyOfPgivenCderivative(prob_pi_given_cj, prob_pi_given_cj_derivative)
        # entropy_p_given_c = self.entropyPgivenC(prob_ck, entropy_of_p_given_c)
        entropy_p_given_c_derivative = self.entropyPgivenCderivative(prob_ck_derivative, entropy_of_p_given_c, prob_ck, entropy_of_p_given_c_derivative)
        # # print np.array(cdfs_cj_pi)  # First index = Class, second index = Feature
        # # print np.array(pdfs_cj_pi)
        # print np.array(cdfs_pi_cj)  # First index = Feature, second index = Class
        # print np.array(pdfs_pi_cj)
        # # print np.array(prob_pi_given_cj)  # First index = Predicted, second index = Class
        # print np.array(prob_pi_given_cj_derivative)  # First index = Derivative
        # print np.array(prob_pi)  # First index = Predicted
        # print np.array(prob_pi_derivative)
        # # print np.array(prob_ck)  # First index = Class
        # print np.array(prob_ck_derivative)
        # # print np.array(entropy_p)
        # print np.array(entropy_p_derivative)
        # # print np.array(entropy_of_p_given_c)  # First index = Class
        # print np.array(entropy_of_p_given_c_derivative)
        # # print np.array(entropy_p_given_c)
        # print np.array(entropy_p_given_c_derivative)
        result = self.mutualInformation(entropy_p_derivative, entropy_p_given_c_derivative)
        del cdfs_cj_pi
        del pdfs_cj_pi
        del cdfs_pi_cj
        del pdfs_pi_cj
        del prob_pi_given_cj
        del prob_pi_given_cj_derivative
        del prob_pi
        del prob_pi_derivative
        del prob_ck
        del prob_ck_derivative
        del entropy_p_derivative
        del entropy_of_p_given_c
        del entropy_of_p_given_c_derivative
        del entropy_p_given_c_derivative
        return result
        # return [self.mutualInformation(thresholds, d) for d in range(self.n_classes)]

    def product(self, iterable):
        return reduce(operator.mul, iterable, 1)

    def pdf(self, t, parameters):
        return scipy.stats.skewnorm.pdf(t, *parameters)

    def cdf(self, t, parameters):
        # return scipy.stats.skewnorm.cdf(t, *parameters)  # same but leaks memory
        alpha, mean, sigma = parameters
        return np.asscalar(np.array(self.sn_r_library.psn(t, xi=mean, alpha=alpha, omega=sigma)))

    # def mutualInformation(self, ts, derivative_index=-1):
    #     if derivative_index == -1:
    #         return self.entropyP(ts, -1) - self.entropyPgivenC(ts, -1)
    #     else:
    #         return self.entropyPderivative(ts, derivative_index) - self.entropyPgivenCderivative(ts, derivative_index)
    #
    # def entropyP(self, ts, derivative_index):
    #     return -sum(prob*np.log2(prob) for prob in (self.probPi(ts, i, -1) for i in range(self.n_classes)))
    #     # sum = 0
    #     # for i in range(self.n_classes):
    #     #     prob = self.probPi(ts, i, derivative_index)
    #     #     sum += -prob*np.log2(prob)
    #     # # print "entropy", sum
    #     # return sum
    #
    # # def entropyOrDerivative(self, ts, func, derivative_index):
    # #     if derivative_index == -1:
    # #         return self.entropy(ts, func, derivative_index)
    # #     else:
    # #         return self.entropyDerivative(ts, func, derivative_index)
    #
    # # def entropyP(self, ts, derivative_index):
    # #     return self.entropyOrDerivative(ts, self.probPi, derivative_index)
    #
    # def entropyPderivative(self, ts, derivative_index):
    #     return -sum(prob_derivative*((np.log(prob)+1)/np.log(2)) for prob, prob_derivative in ((self.probPi(ts, i, -1), self.probPi(ts, i, derivative_index)) for i in range(self.n_classes)))
    #     # sum = 0
    #     # for i in range(self.n_classes):
    #     #     prob = self.probPi(ts, i, -1)
    #     #     prob_derivative = self.probPi(ts, i, derivative_index)
    #     #     sum += -prob_derivative*((np.log(prob) + 1)/np.log(2))
    #     # # print "entropyDerivative", sum
    #     # return sum
    #
    # def entropyOfPgivenC(self, ts, parameters, derivative_index):
    #     return -sum(prob*np.log2(prob) for prob in (self.probPiGivenCj(ts, i, parameters, -1) for i in range(self.n_classes)))
    #     # sum = 0
    #     # for i in range(self.n_classes):
    #     #     prob = self.probPiGivenCj(ts, i, parameters, derivative_index)
    #     #     sum += -prob*np.log2(prob)
    #     # # print "entropyDerivative", sum
    #     # return sum
    #
    # def entropyOfPgivenCderivative(self, ts, parameters, derivative_index):
    #     return -sum(prob_derivative*((np.log(prob)+1)/np.log(2)) for prob, prob_derivative in ((self.probPiGivenCj(ts, i, parameters, -1), self.probPiGivenCj(ts, i, parameters, derivative_index)) for i in range(self.n_classes)))
    #     # sum = 0
    #     # for i in range(self.n_classes):
    #     #     prob = self.probPiGivenCj(ts, i, parameters, -1)
    #     #     prob_derivative = self.probPiGivenCj(ts, i, parameters, derivative_index)
    #     #     sum += -prob_derivative*((np.log(prob) + 1)/np.log(2))
    #     # # print "entropyDerivative", sum
    #     # return sum
    #
    # def entropyPgivenCderivative(self, ts, derivative_index):  # TODO: Check minus
    #     return sum(
    #         prob_ck_derivative*inner_sum + prob_ck*inner_sum_derivative
    #         for inner_sum, inner_sum_derivative, prob_ck, prob_ck_derivative in ((
    #             self.entropyOfPgivenC(ts, self.parameters_cj_pi[j], -1),
    #             self.entropyOfPgivenCderivative(ts, self.parameters_cj_pi[j], derivative_index),
    #             self.probCk(ts, j, -1),
    #             self.probCk(ts, j, derivative_index)
    #         ) for j in range(self.n_classes))
    #     )
    #     # sum = 0
    #     # for j in range(self.n_classes):
    #     #     inner_sum = self.entropyOfPgivenC(ts, self.parameters_cj_pi[j], -1)
    #     #     inner_sum_derivative = self.entropyOfPgivenCderivative(ts, self.parameters_cj_pi[j], derivative_index)
    #     #     prob_ck = self.probCk(ts, j, -1)
    #     #     prob_ck_derivative = self.probCk(ts, j, derivative_index)
    #     #     sum += prob_ck_derivative*inner_sum + prob_ck*inner_sum_derivative
    #     #     # print "entropyPgivenC", sum
    #     # return sum
    #
    # def entropyPgivenC(self, ts, derivative_index):
    #     return sum(inner_sum*prob for inner_sum, prob in ((self.entropyOfPgivenC(ts, self.parameters_cj_pi[j], -1), self.probCk(ts, j, -1)) for j in range(self.n_classes)))
    #     # sum = 0
    #     # for j in range(self.n_classes):
    #     #     inner_sum = self.entropyOfPgivenC(ts, self.parameters_cj_pi[j], -1)
    #     #     sum += inner_sum*self.probCk(ts, j, -1)
    #     # # print "entropyPgivenC", sum
    #     # return -sum
    #
    # def probPiGivenCj(self, xs, p, parameters, derivative_index):
    #     return self.product(
    #         ((1-self.cdf(x, param) if derivative_index != i else -self.pdf(x, param)) if i == p else
    #          (self.cdf(x, param) if derivative_index != i else self.pdf(x, param)))
    #         for i, (param, x) in enumerate(zip(parameters, xs))
    #     )
    #     # product = 1.0
    #     # for i, (param, x) in enumerate(zip(parameters, xs)):
    #     #     if i == p:
    #     #         product *= ((1-self.cdf(x, param)) if derivative_index != i else -self.pdf(x, param))
    #     #     else:
    #     #         product *= (self.cdf(x, param) if derivative_index != i else self.pdf(x, param))
    #     #     # print "probPiGivenCj", product
    #     # return product
    #
    # def probPi(self, xs, p, derivative_index):
    #     return sum(self.probPiGivenCj(xs, p, parameters_cj_pi, derivative_index)*class_proba for j, (parameters_cj_pi, class_proba) in enumerate(zip(self.parameters_cj_pi, self.class_probas)))
    #     # sum = 0.0
    #     # for j, (parameters_cj_pi, class_proba) in enumerate(zip(self.parameters_cj_pi, self.class_probas)):
    #     #     sum += self.probPiGivenCj(xs, p, parameters_cj_pi, derivative_index)*class_proba
    #     # # print "probPi", sum
    #     # return sum
    #
    # def probCk(self, xs, k, derivative_index):
    #     return sum(self.probPiGivenCj(xs, i, self.parameters_cj_pi[k], derivative_index)*self.class_probas[k] for i in range(self.n_classes))
    #     # sum = 0.0
    #     # for i in range(self.n_classes):
    #     #     sum += self.probPiGivenCj(xs, i, self.parameters_cj_pi[k], derivative_index)*self.class_probas[k]
    #     # # print "probCk", sum
    #     # return sum