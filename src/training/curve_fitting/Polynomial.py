import numpy as np
import warnings
import matplotlib.pyplot as plt

from training.curve_fitting import CurveFitting


class PrecisionCurveFitter(CurveFitting.CurveFitting):
    def __init__(self):
        CurveFitting.CurveFitting.__init__(self)
        warnings.simplefilter('ignore', np.RankWarning)

    def getCurve(self, thresholds, values):
        return PrecisionCurve(thresholds, values)


class PredictionCurveFitter(CurveFitting.CurveFitting):
    def __init__(self):
        CurveFitting.CurveFitting.__init__(self)
        warnings.simplefilter('ignore', np.RankWarning)

    def getCurve(self, thresholds, values):
        return PredictionsCurve(thresholds, values)


class PrecisionOrPredictionCurve(CurveFitting.Curve):
    def __init__(self, thresholds, values):
        CurveFitting.Curve.__init__(self)
        self.x = thresholds
        self.y = values
        self.coefficients = None
        self.degree = 20
        self.repeating_threshold = None
        self.fitCurve()

    def makeFunction(self, *args):
        raise NotImplementedError("makeFunction not implemented")

    def makeDerivative(self, x):
        raise NotImplementedError("makeDerivative not implemented")

    def findThresholdWhereValuesStartRepeating(self):
        last_element = self.y[-1]
        if last_element == 0 or last_element == 1:
            return self.x[np.where(self.y == last_element)[0][0]]
        else:
            return self.x[len(self.y)-1]

    def calculateCoefficients(self, thresholds, values):
        return np.polyfit(thresholds, values, self.degree)

    def fitCurve(self):
        self.repeating_threshold = self.findThresholdWhereValuesStartRepeating()
        x_values = np.linspace(self.x[0], self.repeating_threshold, 10000)
        x_values = np.insert(x_values, np.searchsorted(x_values, self.x), self.x)
        x_values = np.unique(x_values)
        values = np.interp(x_values, self.x, self.y)
        self.coefficients = self.calculateCoefficients(x_values, values)
        # self.coefficients = self.calculateCoefficients(self.thresholds, self.values)
        # print self.coefficients
        # print [str(p) + " x^" + str(self.degree-i) + " + " for i, p in enumerate(self.coefficients)]
        # print [str(p) + " * " + str(self.degree-i) + " x^" + str(self.degree-1-i) for i, p in enumerate(self.coefficients[:-1])]
        self.fit_function = self.makeFunction
        self.fit_function_derivative = self.makeDerivative
        return self.fit_function, self.fit_function_derivative

    def plotActualCurve(self):
        plt.ylim(0, 1.1)
        plt.plot(self.x, self.y)

    def plotFitCurve(self):
        points = np.linspace(self.x[0], self.x[-1], 300)
        plt.plot(points, self.fit_function(points))

    def plotFunction(self):
        self.plotActualCurve()
        self.plotFitCurve()

    def plotDerivative(self):
        points = np.linspace(self.x[0], self.x[-1], 300)
        plt.plot(points, self.fit_function_derivative(points))


class PrecisionCurve(PrecisionOrPredictionCurve):
    def makeFunction(self, x):
        return np.where(x < self.repeating_threshold, sum(p*x**(self.degree-i) for i, p in enumerate(self.coefficients)), self.y[-1])

    def makeDerivative(self, x):
        return np.where(x < self.repeating_threshold, sum(p*x**(self.degree-1-i)*(self.degree-i) for i, p in enumerate(self.coefficients[:-1])), 0)


class PredictionsCurve(PrecisionOrPredictionCurve):
    def makeFunction(self, x):
        return sum(p*x**(self.degree-i) for i, p in enumerate(self.coefficients))

    def makeDerivative(self, x):
        return sum(p*x**(self.degree-1-i)*(self.degree-i) for i, p in enumerate(self.coefficients[:-1]))
