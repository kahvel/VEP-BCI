import numpy as np
import matplotlib2tikz
import matplotlib.pyplot as plt


class AbstractCurveFitting(object):
    def fitCurves(self, *args):
        raise NotImplementedError("fitCurves not implemented!")


class CurveFitting(AbstractCurveFitting):
    def __init__(self):
        AbstractCurveFitting.__init__(self)
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

    def fitCurves(self, *args):
        self.calculateCurves(*args)
        # self.plotCurves([0,1,2])
        return (
            self.extractFunctions(),
            self.extractDerivatives(),
        )

    def getCurve(self, *args):
        raise NotImplementedError("getCurve not implemented!")

    def calculateCurves(self, *args):
        self.curves = []
        for arg in zip(*args):
            self.curves.append(self.getCurve(*arg))

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
