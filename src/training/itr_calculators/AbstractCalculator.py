import numpy as np


class ValuesHandler(object):
    def __init__(self, values, fit_curves, fit_curve_derivative):
        self.values = values
        self.fit_curves = fit_curves
        self.fit_curve_derivative = fit_curve_derivative

    def getValueFromCurve(self, curves, xs):
        return np.array([np.asscalar(func(x)) for func, x in zip(curves, xs)])

    def getValueAt(self, xs):
        raise NotImplementedError("getValueAt not implemented!")

    def getDerivativeValueAt(self, x):
        raise NotImplementedError("getDerivativeValueAt not implemented!")


class ItrCalculator(object):
    def __init__(self, window_length, step, feature_maf_length, proba_maf_length, look_back_length, n_targets):
        self.window_length = window_length
        self.step = step
        self.feature_maf_length = feature_maf_length
        self.proba_maf_length = proba_maf_length
        self.look_back_length = look_back_length
        self.n_targets = n_targets
        self.all_predicted_scores = None
        self.n_samples = None
        self.labels = None

    def fitCurves(self, *args):
        raise NotImplementedError("fitCurves not implemented!")

    def calculateCurves(self, *args):
        raise NotImplementedError("calculateCurves not implemented!")

    def setValues(self, all_predicted_scores, labels):
        self.all_predicted_scores = all_predicted_scores
        self.labels = labels
        self.n_samples = len(self.all_predicted_scores[0])

    def gradient(self, thresholds):
        raise NotImplementedError("gradient not implemented!")

    def dMDT_dr(self, r):
        return -self.step/r**2

    def mdt(self, r):
        return self.window_length + (self.look_back_length + self.feature_maf_length + self.proba_maf_length + 1.0/r - 4)*self.step

    def actualItr(self, current_thresholds):
        over_threshold = np.transpose([np.array(pred) > thresh for pred, thresh in zip(self.all_predicted_scores, current_thresholds)])
        counts = over_threshold.sum(1)
        sum_1 = np.where(counts == 1)
        prediction_count = float(sum_1[0].shape[0])
        if prediction_count == 0:
            return 0
        else:
            accuracy = np.logical_and(self.labels[sum_1, :], over_threshold[sum_1, :]).sum()/prediction_count
            predictions = prediction_count/float(self.n_samples)
            return self.itrBitPerMin(accuracy, predictions)

    def itrBitPerMin(self, a, r):
        if r == 0:
            return 0
        else:
            return self.itrBitPerTrial(a)*60.0/self.mdt(r)

    def itrBitPerTrial(self, a):
        if self.n_targets == 1:
            return np.nan
        elif a == 1:
            return np.log2(self.n_targets)
        elif a == 0:
            return np.log2(self.n_targets)+np.log2(1.0/(self.n_targets-1))
        else:
            return np.log2(self.n_targets)+a*np.log2(a)+(1-a)*np.log2((1.0-a)/(self.n_targets-1))

    def itrFromThresholds(self, thresholds):
        raise NotImplementedError("itrFromThresholds not implemented!")
