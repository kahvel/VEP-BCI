import numpy as np
from scipy import pi
from scipy.special import erf
import scipy.optimize
import scipy.stats
import matplotlib.pyplot as plt
from rpy2.robjects.packages import importr

from training.curve_fitting import CurveFitting


class DistributioCurveFitting(CurveFitting.CurveFitting):
    def getCurve(self, features):
        return PdfCurve(features)


class PdfCurve(CurveFitting.Curve):
    def __init__(self, all_features):
        CurveFitting.Curve.__init__(self)
        bar_width = 0.02
        self.all_features = all_features
        # self.bins = int((np.max(all_features)-np.min(all_features))/bar_width)
        self.bins = 50
        self.parameters = None
        hist, bin_edges = np.histogram(self.all_features, bins=self.bins, density=True)
        bin_edges = self.moving_average(bin_edges, 2)
        self.x = bin_edges
        self.y = hist
        self.sn_r_library = importr("sn")
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
        # return scipy.stats.skewnorm.cdf(x, *self.parameters)
        alpha, mean, sigma = self.parameters
        return [np.asscalar(np.array(self.sn_r_library.psn(t, xi=mean, alpha=alpha, omega=sigma))) for t in x]

    def makeDerivative(self, x):
        return scipy.stats.skewnorm.pdf(x, *self.parameters)

    # def makeFunction(self, x):
    #     return scipy.stats.laplace.cdf(x, *self.parameters)
    #
    # def makeDerivative(self, x):
    #     return scipy.stats.laplace.pdf(x, *self.parameters)

    # def makeFunction(self, x):
    #     a, b, loc, scale = self.parameters
    #     return scipy.stats.beta.cdf(x, a, b, loc, scale)
    #
    # def makeDerivative(self, x):
    #     a, b, loc, scale = self.parameters
    #     return scipy.stats.beta.pdf(x, a, b, loc, scale)

    # def makeFunction(self, x):
    #     df, loc, scale = self.parameters
    #     return scipy.stats.chi2.cdf(x, loc, scale)
    #
    # def makeDerivative(self, x):
    #     df, loc, scale = self.parameters
    #     return scipy.stats.chi2.pdf(x, loc, scale)

    # def makeFunction(self, x):
    #     loc, scale = self.parameters
    #     return scipy.stats.expon.cdf(x, loc, scale)
    #
    # def makeDerivative(self, x):
    #     loc, scale = self.parameters
    #     return scipy.stats.expon.pdf(x, loc, scale)

    # def makeFunction(self, x):
    #     a, loc, scale = self.parameters
    #     return scipy.stats.gamma.cdf(x, a, loc, scale)
    #
    # def makeDerivative(self, x):
    #     a, loc, scale = self.parameters
    #     return scipy.stats.gamma.pdf(x, loc, scale)

    # def makeFunction(self, x):
    #     degree = len(self.parameters)+1
    #     return sum(p*x**(degree-i) for i, p in enumerate(self.parameters))
    #
    # def makeDerivative(self, x):
    #     degree = len(self.parameters)+1
    #     return sum(p*x**(degree-1-i)*(degree-i) for i, p in enumerate(self.parameters[:-1]))

    # def makeFunction(self, x):
    #     s, loc, scale = self.parameters
    #     return scipy.stats.lognorm.cdf(x, s, loc, scale)
    #
    # def makeDerivative(self, x):
    #     s, loc, scale = self.parameters
    #     return scipy.stats.lognorm.pdf(x, s, loc, scale)

    def fitSkew(self, initial_guess):
        return scipy.optimize.curve_fit(self.skew, self.x, self.y, p0=initial_guess, maxfev=500000)

    def expon(self, x, loc, scale):
        return scipy.stats.expon.pdf(x, loc=loc, scale=scale)

    def laplace(self, x, loc, scale):
        return scipy.stats.laplace.pdf(x, loc=loc, scale=scale)

    def chi2(self, x, df, loc, scale):
        return scipy.stats.chi2.pdf(x, df, loc=loc, scale=scale)

    def lognormal(self, x, s, loc, scale):
        return scipy.stats.lognorm.pdf(x, s, loc=loc, scale=scale)

    def beta(self, x, a, b, loc, scale):
        return scipy.stats.beta.pdf(x, a, b, loc, scale)

    def gamma(self, x, a, loc, scale):
        return scipy.stats.gamma.pdf(x, a, loc, scale)

    def fitLognorm(self, initial_guess):  # also jumps up falls down
        return scipy.optimize.curve_fit(self.lognormal, self.x, self.y, p0=initial_guess, maxfev=500000)

    def fitLaplace(self, initial_guess):  # goes too fast to zero
        return scipy.optimize.curve_fit(self.laplace, self.x, self.y, p0=initial_guess, maxfev=500000)

    def fitExpon(self, initial_guess):  # goes too fast to zero + wiggles
        return scipy.optimize.curve_fit(self.expon, self.x, self.y, p0=initial_guess, maxfev=500000)

    def fitBeta(self, initial_guess):  # cannot fit straight lines, randomly falls down/jumps up
        return scipy.optimize.curve_fit(self.beta, self.x, self.y, p0=initial_guess, maxfev=500000)

    def fitChi2(self, initial_guess):  # cannot get fit at all, maybe wron estimate for df
        return scipy.optimize.curve_fit(self.chi2, self.x, self.y, p0=initial_guess, maxfev=500000)

    def fitGamma(self, initial_guess):
        return scipy.optimize.curve_fit(self.gamma, self.x, self.y, p0=initial_guess, maxfev=500000)

    def fitPoly(self):
        return np.polyfit(self.x, self.y, 4)

    def fitCurve(self):
        self.parameters = self.fitSkew([0, np.mean(self.all_features), np.std(self.all_features)])[0]  # , 0, 1])
        # self.parameters = self.fitBeta([1, 1, np.mean(self.all_features), np.std(self.all_features)])[0]
        # self.parameters = self.fitLaplace([np.mean(self.all_features), np.std(self.all_features)])[0]
        # self.parameters = self.fitExpon([np.mean(self.all_features), np.std(self.all_features)])[0]
        # self.parameters = self.fitChi2([1, np.mean(self.all_features), np.std(self.all_features)])[0]
        # self.parameters = self.fitLognorm([1, np.mean(self.all_features), np.std(self.all_features)])[0]
        # self.parameters = self.fitGamma([1, np.mean(self.all_features), np.std(self.all_features)])[0]
        # median = np.median(self.all_features)
        # self.parameters = [median, np.abs(self.all_features-median).sum()/len(self.all_features)]
        # self.parameters = self.fitPoly()
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
