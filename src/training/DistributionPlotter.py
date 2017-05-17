import numpy as np
import scipy.stats
import scipy.optimize
import pandas as pd
import pandas.tools.plotting
import itertools
import matplotlib.pyplot as plt

from scipy import pi,sqrt,exp
from scipy.special import erf


class Plotter(object):
    def __init__(self, data, labels, thresholds_by_split, ordered_labels):
        self.ordered_labels = ordered_labels
        self.data = data
        self.labels = labels
        self.thresholds_by_split = np.transpose(thresholds_by_split)
        self.mean_thresholds = np.mean(self.thresholds_by_split, 1)
        self.min_feature = np.min(self.data)
        self.max_feature = np.max(self.data)
        self.n_features = len(self.data)
        self.n_classes = len(self.ordered_labels)
        self.bar_width = 0.02
        # self.bins = int((current_max-current_min)/self.bar_width)
        self.bins = 50
        self.colors = ["blue", "green", "red"]
        self.parameters = []

    def plotJointPdfs(self):
        dataframe = pd.DataFrame(self.data, columns=["F_1", "F_2", "F_3"])
        axes = pd.tools.plotting.scatter_matrix(dataframe, hist_kwds={"bins": 100})
        for axes_row in axes:
            for ax, thresholds in zip(axes_row, self.thresholds_by_split):
                ax.plot()
        plt.tight_layout()

    def pair(self):
        only_class = 1
        if only_class is not None:
            data = self.data[np.where(self.labels == only_class)]
        else:
            data = self.data
        fig = plt.figure()
        y_min = 0
        y_max = 100
        for i in range(self.n_classes):
            for j in range(self.n_classes):
                nSub = i * self.n_classes + j + 1
                ax = fig.add_subplot(self.n_classes, self.n_classes, nSub)
                if i == j:
                    current_min = np.min(data[:,i])
                    current_max = np.max(data[:,i])
                    ax.set_xlim((self.min_feature, self.max_feature))
                    ax.set_ylim((y_min, y_max))
                    ax.hist(data[:,i], bins=self.bins, normed=False, color=self.colors[i])
                    ax.plot([self.mean_thresholds[i], self.mean_thresholds[i]], [y_min, y_max], color=self.colors[i])
                    ax.set_title(self.labels[i])
                else:
                    ax.set_xlim((self.min_feature, self.max_feature))
                    ax.set_ylim((self.min_feature, self.max_feature))
                    # ax.plot(data[:,i], data[:,j], '.k', alpha=0.2)
                    if only_class is None:
                        for k, class_label in enumerate(self.ordered_labels):
                            indices = np.where(self.labels == class_label)
                            ax.plot(data[indices,j], data[indices,i], ".k", alpha=0.2, color=self.colors[k])
                    else:
                        ax.plot(data[:,j], data[:,i], ".k", alpha=0.2)
                    ax.plot([self.mean_thresholds[j], self.mean_thresholds[j]], [self.min_feature, self.max_feature], color=self.colors[j])
                    ax.plot([self.min_feature, self.max_feature], [self.mean_thresholds[i], self.mean_thresholds[i]], color=self.colors[i])
                    # for threshold in self.thresholds_by_split[i]:
                    #     ax.plot([threshold, threshold], [self.min_feature, self.max_feature])
                    # for threshold in self.thresholds_by_split[j]:
                    #     ax.plot([self.min_feature, self.max_feature], [threshold, threshold])
        plt.tight_layout()
        return fig

    def fitSkew(self, data, initial_guess):
        return scipy.optimize.leastsq(self.func, initial_guess, (data,), maxfev=10000)

    def pdf(self, x):
        return 1.0/sqrt(2*pi) * exp(-x**2/2.0)

    def cdf(self, x):
        return (1 + erf(x/sqrt(2))) / 2.0

    def skew(self, parameters, x):
        e, w, a = parameters
        t = (x-e) / float(w)
        return 2.0 / w * self.pdf(t) * self.cdf(a*t)

    def func(self, x, alpha, mu, sigma):  # , c, a):
        normpdf = (1.0/(sigma*np.sqrt(2*pi)))*np.exp(-(np.power((x-mu),2)/(2.0*np.power(sigma,2))))
        normcdf = (0.5*(1.0+erf((alpha*((x-mu)/sigma))/(np.sqrt(2.0)))))
        return 2.0*normpdf*normcdf
        # return 2*a*normpdf*normcdf + c

    def plotSkew(self, data, current_min, current_max):
        # mean = np.mean(data)
        parameters = self.fitSkew2(data, current_min, current_max, [0, np.mean(data), np.std(data)])  # , 0, 1])
        # parameters = self.fitTest(data, current_min, current_max, [np.mean(data), np.std(data)])
        parameters = parameters[0]
        self.parameters.append(parameters)
        # print self.func(data, *parameters)
        # print self.skew(parameters, data)
        points = np.linspace(current_min, current_max, len(data))
        # plt.plot(points, self.skewNorm(points, *parameters))
        plt.plot(points, self.func(points, *parameters))
        # plt.plot(points, scipy.stats.norm.pdf(points, *parameters))

    def plotSkewCdf(self, data, parameters):
        current_min = np.min(data)
        current_max = np.max(data)
        points = np.linspace(current_min, current_max, len(data))
        plt.plot(points, 1-scipy.stats.skewnorm.cdf(points, *parameters))

    def fitTest(self, data, current_min, current_max, initial_guess):
        hist, bin_edges = np.histogram(data, bins=self.bins, density=True)
        bin_edges = self.moving_average(bin_edges, 2)
        return scipy.optimize.curve_fit(scipy.stats.norm.pdf, bin_edges, hist, p0=initial_guess)

    def moving_average(self, a, n) :
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def skewNorm(self, data, alpha, mu, sigma):
        y = (data - mu) / float(sigma)
        return scipy.stats.skewnorm.pdf(y, alpha)

    def fitSkew2(self, data, current_min, current_max, initial_guess):
        hist, bin_edges = np.histogram(data, bins=self.bins, density=True)
        bin_edges = self.moving_average(bin_edges, 2)
        return scipy.optimize.curve_fit(self.func, bin_edges, hist, p0=initial_guess)

    def plotNorm(self, data, current_min, current_max):
        mean = np.mean(data)
        std = np.std(data)
        points = np.linspace(current_min, current_max, len(data))
        plt.plot(points, scipy.stats.norm.pdf(points, mean, std))

    def plotPdf(self):
        y_min = 0
        y_max = 8
        plt.figure()
        for i, true_class in enumerate(self.ordered_labels):
            features_given_class = np.transpose(self.data[np.where(self.labels == true_class)])
            for j, (features, thresholds) in enumerate(zip(features_given_class, self.thresholds_by_split)):
                plt.subplot(self.n_classes, self.n_classes, i*self.n_classes+j+1)
                plt.xlim(self.min_feature, self.max_feature)
                plt.ylim(y_min, y_max)
                for threshold in thresholds:
                    plt.plot([threshold, threshold], [y_min, y_max], color="red")
                if j == 0 or True:
                    plt.title("P(F_"+str(j+1)+"|C)")
                if i == 0 or True:
                    plt.ylabel("C="+str(true_class))
                current_min = np.min(features)
                current_max = np.max(features)
                # print current_max, current_min, (current_max-current_min), (current_max-current_min)/0.005
                plt.hist(features, bins=self.bins, normed=True)
                self.plotSkew(features, current_min, current_max)
        plt.tight_layout()

    def plotCdf1(self):
        plt.figure()
        for j, features in enumerate(np.transpose(self.data)):
            thresholds = np.unique(features)
            cdf = (self.n_features + 1.0 - np.sort(features).searchsorted(thresholds, side="right"))/self.n_features
            plt.subplot(self.n_classes, self.n_classes, j+1)
            plt.title("f(t)=P(F_"+str(j+1)+">=t)")
            plt.plot(thresholds, cdf)
        plt.tight_layout()

    def plotCdf(self):
        plt.figure()
        for i, true_class in enumerate(self.ordered_labels):
            features_given_class = np.transpose(self.data[np.where(self.labels == true_class)])
            for j, (features, pred_thresholds) in enumerate(zip(features_given_class, self.thresholds_by_split)):
                thresholds = np.unique(features)
                n_features = features.shape[0]
                cdf = (n_features + 1.0 - np.sort(features).searchsorted(thresholds, side="right"))/n_features
                plt.subplot(self.n_classes, self.n_classes, i*self.n_classes+j+1)
                for threshold in pred_thresholds:
                    plt.plot([threshold, threshold], [0, 1.1], color="red")
                plt.title("f(t)=P(F_"+str(j+1)+">=t|C)")
                plt.ylabel("C="+str(true_class))
                plt.ylim((0, 1.1))
                plt.xlim((self.min_feature, self.max_feature))
                thresholds = np.insert(thresholds, 0, self.min_feature)
                cdf = np.insert(cdf, 0, 1)
                plt.plot(thresholds, cdf)
                plt.fill_between(thresholds, cdf, alpha=0.1)
                self.plotSkewCdf(features, self.parameters[i*self.n_classes+j])
        plt.tight_layout()

    def plotJointCdf(self):
        plt.figure()
        cdfs = []
        for j, features in enumerate(np.transpose(self.data)):
            thresholds = np.unique(features)
            cdfs.append((self.n_features + 1.0 - np.sort(features).searchsorted(thresholds, side="right"))/self.n_features)
        for i, (cdf1, cdf2) in enumerate(itertools.combinations(cdfs, 2)):
            plt.subplot(self.n_classes, self.n_classes, i+1)
            plt.title("")
            plt.plot(cdf1, cdf2, "o")
        plt.tight_layout()