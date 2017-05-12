import numpy as np
from scipy import pi
from scipy.special import erf
import scipy.optimize
import scipy.stats
import matplotlib.pyplot as plt

from training.curve_fitting import CurveFitting


class DistributioCurveFitting(CurveFitting.CurveFitting):
    def getCurve(self, features):
        return PdfCurve(features)


class PdfCurve(CurveFitting.Curve):
    def __init__(self, all_features):
        CurveFitting.Curve.__init__(self)
        bar_width = 0.02
        self.all_features = all_features
        self.bins = int((np.max(all_features)-np.min(all_features))/bar_width)
        self.parameters = None
        hist, bin_edges = np.histogram(self.all_features, bins=self.bins, density=True)
        bin_edges = self.moving_average(bin_edges, 2)
        self.x = bin_edges
        self.y = hist
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
        return scipy.optimize.curve_fit(self.skew, self.x, self.y, p0=initial_guess)

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
