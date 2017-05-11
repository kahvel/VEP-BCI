import numpy as np
from scipy import pi
from scipy.special import erf
import scipy.optimize
import scipy.stats
import matplotlib2tikz
import matplotlib.pyplot as plt
import warnings


class CurveFitting(object):
    def __init__(self):
        self.curves = []

    def plotCurves(self, classes):
        for i, curve in enumerate(self.curves):
            if i in classes:
                plt.figure()
                plt.subplot(121)
                curve.plotFunction()
                plt.subplot(122)
                curve.plotDerivative()
        # plt.show()
        # import time
        # matplotlib2tikz.save("C:\\Users\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\file" + str(round(time.time())) + ".tex")
        # raw_input()
        # matplotlib2tikz.save("C:\\Users\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\file" + str(round(time.time())) + "1.tex")
        # plt.figure()
        # plt.plot(points, precision_derivative(points))
        # plt.plot(points, prediction_derivative(points))
        # plt.figure()
        # plt.plot(points, precision_derivative(points))
        # differences = np.diff(thresholds)
        # differences = np.gradient(precisions, np.insert(differences, len(differences)-1, differences[-1]))
        # plt.plot(thresholds, np.gradient(precisions))
        # plt.figure()
        # plt.plot(points, prediction_derivative(points))
        # plt.plot(thresholds, np.gradient(predictions))
        # print np.gradient(precisions)
        # print np.gradient(predictions)

    def fitCurves(self, array1, array2):
        self.calculateCurves(array1, array2)
        # self.plotCurves([1])
        return (
            self.extractFunctions(),
            self.extractDerivatives(),
        )

    def getCurve(self, array1, array2):
        raise NotImplementedError("getCurve not implemented!")

    def calculateCurves(self, array1, array2):
        self.curves = []
        for ar1, ar2 in zip(array1, array2):
            self.curves.append(self.getCurve(ar1, ar2))

    def extract(self, curves, extractor):
        return [extractor(curve) for curve in curves]

    def functionExtractor(self, curve):
        return curve.fit_function

    def derivativeExtractor(self, curve):
        return curve.fit_function_derivative

    def extractFunctions(self):
        return self.extract(self.curves, self.functionExtractor)

    def extractDerivatives(self):
        return self.extract(self.curves, self.derivativeExtractor)


class PrecisionCurveFitter(CurveFitting):
    def __init__(self):
        CurveFitting.__init__(self)
        warnings.simplefilter('ignore', np.RankWarning)

    def getCurve(self, thresholds, values):
        return PrecisionCurve(thresholds, values)


class PredictionCurveFitter(CurveFitting):
    def __init__(self):
        CurveFitting.__init__(self)
        warnings.simplefilter('ignore', np.RankWarning)

    def getCurve(self, thresholds, values):
        return PredictionsCurve(thresholds, values)


class Curve(object):
    def __init__(self):
        self.x = None
        self.y = None
        self.fit_function = None
        self.fit_function_derivative = None

    def plotFunction(self):
        raise NotImplementedError("plotFunction not implemented!")

    def plotDerivative(self):
        raise NotImplementedError("plotDerivative not implemented!")


class PrecisionOrPredictionCurve(Curve):
    def __init__(self, thresholds, values):
        Curve.__init__(self)
        self.x = thresholds
        self.y = values
        self.coefficients = None
        self.degree = 20
        self.repeating_threshold = None
        self.fitCurve()

    def makeFunction(self, x):
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


class PdfCurve(Curve):
    def __init__(self, all_features, all_labels):
        Curve.__init__(self)
        bar_width = 0.02
        self.all_features = all_features
        self.bins = int((np.max(all_features)-np.min(all_features))/bar_width)
        self.all_labels = all_labels
        self.parameters = None
        self.fitCurve()

    def moving_average(self, a, n) :
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def skew(self, x, alpha, mu, sigma):  # , c, a):
        normpdf = (1.0/(sigma*np.sqrt(2*pi)))*np.exp(-(np.power((x-mu),2)/(2.0*np.power(sigma,2))))
        normcdf = (0.5*(1.0+erf((alpha*((x-mu)/sigma))/(np.sqrt(2.0)))))
        return 2.0*normpdf*normcdf
        # return 2*a*normpdf*normcdf + c

    def makeFunction(self, x):
        return scipy.stats.skewnorm.cdf(x, *self.parameters)

    def makeDerivative(self, x):
        return scipy.stats.skewnorm.pdf(x, *self.parameters)

    def fitSkew(self, initial_guess):
        hist, bin_edges = np.histogram(self.all_features, bins=self.bins, density=True)
        bin_edges = self.moving_average(bin_edges, 2)
        self.x = bin_edges
        self.y = hist
        return scipy.optimize.curve_fit(self.skew, bin_edges, hist, p0=initial_guess)

    def fitCurve(self):
        self.parameters = self.fitSkew([0, np.mean(self.all_features), np.std(self.all_features)])[0]  # , 0, 1])
        self.fit_function = self.makeFunction
        self.fit_function_derivative = self.makeDerivative
        return self.fit_function, self.fit_function_derivative

    def plotActualCurve(self):
        plt.plot(self.x, self.y)

    def plotFunction(self):
        points = np.linspace(self.x[0], self.x[-1], 300)
        plt.plot(points, self.fit_function(points))

    def plotFitCurve(self):
        points = np.linspace(self.x[0], self.x[-1], 300)
        plt.plot(points, self.fit_function_derivative(points))

    def plotDerivative(self):
        self.plotActualCurve()
        self.plotFitCurve()


class DistrubutionCurveFitting(CurveFitting):
    def getCurve(self, all_features, all_labels):
        return PdfCurve(all_features, all_labels)
