import numpy as np


class ItrCalculator(object):
    def __init__(self, window_length, step, feature_maf_length, proba_maf_length, look_back_length, n_targets):
        self.window_length = window_length
        self.step = step
        self.feature_maf_length = feature_maf_length
        self.proba_maf_length = proba_maf_length
        self.look_back_length = look_back_length
        self.n_targets = n_targets

    def derivative(self, precisions, relative_support_per_class):
        return (
            self.itrMinDerivativePrecision(precisions, relative_support_per_class),
            self.itrMinDerivativeSupportPerClass(precisions, relative_support_per_class)
        )

    def accuracyDerivativePrecision(self, relative_support_per_class):
        return np.array(relative_support_per_class)

    def accuracyDerivativeSupportPerClass(self, precisions):
        return np.array(precisions)

    def supportDerivative(self):
        return np.ones(self.n_targets)

    def mdtDerivative(self, relative_support):
        return -self.step/relative_support**2

    def itrTrialDerivative(self, accuracy):
        return np.log2(accuracy * (self.n_targets - 1.0) / (1.0 - accuracy))

    def itrMinDerivativeAccuracy(self, accuracy, relative_support):
        return self.itrTrialDerivative(accuracy) * 60.0 / self.mdt(relative_support)

    def itrMinDerivativeSupport(self, accuracy, relative_support):
        return -self.mdtDerivative(relative_support)/self.mdt(relative_support)**2*self.itrBitPerTrial(accuracy)*60.0

    def itrMinDerivativePrecision(self, precisions, relative_support_per_class):
        accuracy = self.accuracy(precisions, relative_support_per_class)
        relative_support = self.relativeSupport(relative_support_per_class)
        return self.itrMinDerivativeAccuracy(accuracy, relative_support)*self.accuracyDerivativePrecision(relative_support_per_class)

    def itrMinDerivativeSupportPerClass(self, precisions, relative_support_per_class):
        accuracy = self.accuracy(precisions, relative_support_per_class)
        relative_support = self.relativeSupport(relative_support_per_class)
        return self.itrMinDerivativeAccuracy(accuracy, relative_support)*self.accuracyDerivativeSupportPerClass(precisions) \
               + self.itrMinDerivativeSupport(accuracy, relative_support)*self.supportDerivative()

    def accuracy(self, precisions, relative_support_per_class):
        return sum(map(lambda (p, n): p*n, zip(precisions, relative_support_per_class)))

    def relativeSupport(self, relative_support_per_class):
        return sum(relative_support_per_class)

    def mdt(self, relative_support):
        return self.window_length + (self.look_back_length + self.feature_maf_length + self.proba_maf_length + 1.0/relative_support - 4)*self.step

    def itrBitPerMin(self, accuracy, relative_support):
        if relative_support == 0:
            print "Warning! Relative support 0"
            return 0
        else:
            return self.itrBitPerTrial(accuracy)*60.0/self.mdt(relative_support)

    def itrBitPerTrial(self, accuracy):
        if self.n_targets == 1:
            return np.nan
        elif accuracy == 1:
            return np.log2(self.n_targets)
        elif accuracy == 0:
            print "Warning! accuracy 0"
            return np.nan
        else:
            return np.log2(self.n_targets)+accuracy*np.log2(accuracy)+(1-accuracy)*np.log2((1-accuracy)/(self.n_targets-1))


