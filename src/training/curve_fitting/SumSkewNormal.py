import numpy as np
import matplotlib.pyplot as plt

from training.curve_fitting import CurveFitting, SkewNormal


class SumCurve(object):
    def __init__(self, all_labels, functions, derivatives):
        self.class_probas = np.sum(all_labels, 1)/float(len(all_labels[0]))
        self.functions = functions
        self.derivatives = derivatives
        self.fit_function = self.makeFunction
        self.fit_function_derivative = self.makeDerivative

    def makeFunction(self, x):
        raise NotImplementedError("makeFunction not implemented!")

    def makeDerivative(self, x):
        raise NotImplementedError("makeDerivative not implemented!")


class PdfCurveSum(SumCurve):
    def makeFunction(self, x):
        return sum(function(x)*class_proba for function, class_proba in zip(self.functions, self.class_probas))

    def makeDerivative(self, x):
        return sum(function(x)*class_proba for function, class_proba in zip(self.derivatives, self.class_probas))


class ProbPi(SumCurve):
    def __init__(self, all_labels, functions, derivatives, i):
        SumCurve.__init__(self, all_labels, functions, derivatives)
        self.functions = np.transpose(functions)
        self.derivatives = np.transpose(derivatives)
        self.p = i

    def makeFunction(self, xs):
        sum = 0.0
        for j, (functions_cj_fi, class_proba) in enumerate(zip(self.functions, self.class_probas)):
            product = 1.0
            for i, (function_cj_fi, x) in enumerate(zip(functions_cj_fi, xs)):
                if i == self.p:
                    product *= (1-function_cj_fi(x))
                else:
                    product *= function_cj_fi(x)
            sum += product*class_proba
        return sum

    def makeOneDerivative(self, xs, derivative_index):
        sum = 0.0
        for j, (functions_cj_fi, derivatives, class_proba) in enumerate(zip(self.functions, self.derivatives, self.class_probas)):
            product = 1.0
            for i, (function_cj_fi, derivative, x) in enumerate(zip(functions_cj_fi, derivatives, xs)):
                if i == self.p:
                    product *= ((1-function_cj_fi(x)) if derivative_index != i else -derivative(x))
                else:
                    product *= (function_cj_fi(x) if derivative_index != i else derivative(x))
            sum += product*class_proba
        return sum

    def makeDerivative(self, xs):
        return np.array([self.makeOneDerivative(xs, i) for i in range(len(self.functions))])


class ProbCj(SumCurve):
    def __init__(self, all_labels, functions, derivatives, k):
        SumCurve.__init__(self, all_labels, functions, derivatives)
        self.class_proba = self.class_probas[k]

    def makeFunction(self, xs):
        sum = 0.0
        for i in range(len(self.functions)):
            product = 1.0
            for j, (function_same_c_different_f, x) in enumerate(zip(self.functions, xs)):
                if i == j:
                    product *= (1-function_same_c_different_f(x))
                else:
                    product *= function_same_c_different_f(x)
            sum += product*self.class_proba
        return sum

    def makeOneDerivative(self, xs, derivative_index):
        sum = 0.0
        for i in range(len(self.functions)):
            product = 1.0
            for j, (function_same_c_different_f, derivative, x) in enumerate(zip(self.functions, self.derivatives, xs)):
                if i == j:
                    product *= ((1-function_same_c_different_f(x)) if derivative_index != j else -derivative(x))
                else:
                    product *= (function_same_c_different_f(x) if derivative_index != j else derivative(x))
            sum += product*self.class_proba
        return sum

    def makeDerivative(self, xs):
        return np.array([self.makeOneDerivative(xs, i) for i in range(len(self.functions))])


class DistrubutionSumCurves(CurveFitting.AbstractCurveFitting):
    def __init__(self):
        CurveFitting.AbstractCurveFitting.__init__(self)
        self.sumCurves = []
        self.curves_pi = []
        self.curves_cj = []
        self.curve_fitter = SkewNormal.DistributioCurveFitting()

    def fitCurves(self, all_features, all_labels):
        self.sumCurves = []
        self.curves_pi = []
        self.curves_cj = []
        functions_fi_cj = []
        derivatives_fi_cj = []
        for i, features in enumerate(all_features):
            functions_fi, derivatives_fi = self.curve_fitter.fitCurves([features[np.where(labels)] for labels in all_labels])
            functions_fi_cj.append(functions_fi)
            derivatives_fi_cj.append(derivatives_fi)
        for i, (features, labels) in enumerate(zip(all_features, all_labels)):
            curve = self.getSumCurve(all_labels, functions_fi_cj[i], derivatives_fi_cj[i])
            self.sumCurves.append(curve)
        for i, (features, labels) in enumerate(zip(all_features, all_labels)):
            prob_pi = self.getProbPi(all_labels, functions_fi_cj, derivatives_fi_cj, i)
            self.curves_pi.append(prob_pi)
        for j, (features, labels) in enumerate(zip(all_features, all_labels)):
            prob_cj = self.getProbCj(all_labels, np.transpose(functions_fi_cj)[j], np.transpose(derivatives_fi_cj)[j], j)
            self.curves_cj.append(prob_cj)
        ts = 1.3, 1.3, 1.3
        for i, (functions, derivatives, t) in enumerate(zip(functions_fi_cj, derivatives_fi_cj, ts)):
            for j, (function, derivative) in enumerate(zip(functions, derivatives)):
                print "P (F_" + str(i+1) + " < " + str(t) + " | C=" + str(j+1) + ") = " + str(function(t)), "  ", 1-function(t)
                print "p (F_" + str(i+1) + " = " + str(t) + " | C=" + str(j+1) + ") = " + str(derivative(t))
                print
        for i, curve in enumerate(self.curves_pi):
            function = curve.fit_function
            derivatives = curve.fit_function_derivative
            print "P (P = " + str(i+1) + ") = " + str(function(ts))
            print "\t", derivatives(ts)
        for i, curve in enumerate(self.curves_cj):
            function = curve.fit_function
            derivatives = curve.fit_function_derivative
            print "P (C_s = " + str(i+1) + ") = " + str(function(ts))
            print "\t", derivatives(ts)

    def getSumCurve(self, all_labels, functions, derivatives):
        return PdfCurveSum(all_labels, functions, derivatives)

    def getProbPi(self, all_labels, functions, derivatives, i):
        return ProbPi(all_labels, functions, derivatives, i)

    def getProbCj(self, all_labels, functions, derivatives, j):
        return ProbCj(all_labels, functions, derivatives, j)

    def plotCurves(self, classes):
        n_classes = len(self.sumCurves)
        plt.figure()
        for i, curve in enumerate(self.sumCurves):
            plt.subplot(2, n_classes, i+1)
            curve.plotFunction()
            plt.subplot(2, n_classes, n_classes+i+1)
            curve.plotDerivative()
