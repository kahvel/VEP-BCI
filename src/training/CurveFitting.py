import numpy as np
import matplotlib2tikz
import matplotlib.pyplot as plt
import warnings


class CurveFitting(object):
    def __init__(self):
        self.prediction_curves = []
        self.precision_curves = []
        warnings.simplefilter('ignore', np.RankWarning)

    def plotCurves(self, thresholds, precisions, predictions, classes):
        for i, (threshold, precision, prediction, precision_curve, prediction_curve) in enumerate(zip(thresholds, precisions, predictions, self.precision_curves, self.prediction_curves)):
            if i in classes:
                plt.figure()
                plt.subplot(221)
                precision_curve.plotActualAndFitCurve()
                plt.subplot(222)
                prediction_curve.plotActualAndFitCurve()
                plt.subplot(223)
                precision_curve.plotDerivative()
                plt.subplot(224)
                prediction_curve.plotDerivative()
        plt.show()
        # import time
        # matplotlib2tikz.save("C:\\Users\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\file" + str(round(time.time())) + ".tex")
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

    def calculatePrecisionPredictionCurves(self, all_thresholds, all_precisions, all_relative_predictions):
        self.fitCurves(all_thresholds, all_precisions, all_relative_predictions)
        # self.plotCurves(all_thresholds, all_precisions, all_relative_predictions, [0,1,2])
        return (
            self.extractPrecisionFunctions(),
            self.extractPredictionFunctions(),
            self.extractPrecisionDerivatives(),
            self.extractPredictionDerivatives(),
        )

    def fitCurves(self, thresholds, precisions, predictions):
        self.prediction_curves = []
        self.precision_curves = []
        for threshold, precision, prediction in zip(thresholds, precisions, predictions):
            self.prediction_curves.append(Curve(threshold, prediction))
            self.precision_curves.append(PrecisionCurve(threshold, precision))

    def extractFunctions(self, curves, extractor):
        return [extractor(curve) for curve in curves]

    def functionExtractor(self, curve):
        return curve.fit_curve

    def derivativeExtractor(self, curve):
        return curve.fit_curve_derivative

    def extractPrecisionFunctions(self):
        return self.extractFunctions(self.precision_curves, self.functionExtractor)

    def extractPredictionFunctions(self):
        return self.extractFunctions(self.prediction_curves, self.functionExtractor)

    def extractPrecisionDerivatives(self):
        return self.extractFunctions(self.precision_curves, self.derivativeExtractor)

    def extractPredictionDerivatives(self):
        return self.extractFunctions(self.prediction_curves, self.derivativeExtractor)


class Curve(object):
    def __init__(self, thresholds, values):
        self.thresholds = thresholds
        self.values = values
        self.fit_curve = None
        self.fit_curve_derivative = None
        self.coefficients = None
        self.degree = 20
        self.repeating_threshold = None
        self.fitCurve()

    def makeFunction(self, x):
        return sum(p*x**(self.degree-i) for i, p in enumerate(self.coefficients))

    def makeDerivative(self, x):
        return sum(p*x**(self.degree-1-i)*(self.degree-i) for i, p in enumerate(self.coefficients[:-1]))

    def findThresholdWhereValuesStartRepeating(self):
        last_element = self.values[-1]
        if last_element == 0 or last_element == 1:
            return self.thresholds[np.where(self.values == last_element)[0][0]]
        else:
            return self.thresholds[len(self.values)-1]

    def calculateCoefficients(self, thresholds, values):
        return np.polyfit(thresholds, values, self.degree)

    def fitCurve(self):
        self.repeating_threshold = self.findThresholdWhereValuesStartRepeating()
        x_values = np.linspace(self.thresholds[0], self.repeating_threshold, 10000)
        x_values = np.insert(x_values, np.searchsorted(x_values, self.thresholds), self.thresholds)
        x_values = np.unique(x_values)
        values = np.interp(x_values, self.thresholds, self.values)
        self.coefficients = self.calculateCoefficients(x_values, values)
        # print self.coefficients
        # print [str(p) + " x^" + str(self.degree-i) + " + " for i, p in enumerate(self.coefficients)]
        # print [str(p) + " * " + str(self.degree-i) + " x^" + str(self.degree-1-i) for i, p in enumerate(self.coefficients[:-1])]
        self.fit_curve = self.makeFunction
        self.fit_curve_derivative = self.makeDerivative
        return self.fit_curve, self.fit_curve_derivative

    def plotActualCurve(self):
        plt.ylim(0, 1.1)
        plt.plot(self.thresholds, self.values)

    def plotFitCurve(self):
        points = np.linspace(self.thresholds[0], self.thresholds[-1], 300)
        plt.plot(points, self.fit_curve(points))

    def plotActualAndFitCurve(self):
        self.plotActualCurve()
        self.plotFitCurve()

    def plotDerivative(self):
        points = np.linspace(self.thresholds[0], self.thresholds[-1], 300)
        plt.plot(points, self.fit_curve_derivative(points))


class PrecisionCurve(Curve):
    def makeFunction(self, x):
        return np.where(x < self.repeating_threshold, sum(p*x**(self.degree-i) for i, p in enumerate(self.coefficients)), self.values[-1])

    def makeDerivative(self, x):
        return np.where(x < self.repeating_threshold, sum(p*x**(self.degree-1-i)*(self.degree-i) for i, p in enumerate(self.coefficients[:-1])), 0)
