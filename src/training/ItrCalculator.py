import numpy as np


class ItrCalculator(object):
    def __init__(self, window_length, step, feature_maf_length, proba_maf_length, look_back_length, n_targets):
        self.window_length = window_length
        self.step = step
        self.feature_maf_length = feature_maf_length
        self.proba_maf_length = proba_maf_length
        self.look_back_length = look_back_length
        self.n_targets = n_targets

    def derivative(self, precisions, relative_predictions_per_class, dp, dr):
        return dp*self.itrMinDerivativePrecision(precisions, relative_predictions_per_class) +\
               dr*self.itrMinDerivativePredictionsPerClass(precisions, relative_predictions_per_class)

    def accuracy(self, precisions, relative_predictions_per_class):
        return sum(map(lambda (p, n): p*n, zip(precisions, relative_predictions_per_class)))

    def accuracyDerivativePrecision(self, relative_predictions_per_class):
        return np.array(relative_predictions_per_class)

    def accuracyDerivativePredictionsPerClass(self, precisions, relative_predictions_per_class):
        return np.array(precisions)

    def predictionsDerivative(self):
        return np.ones(self.n_targets)

    def mdtDerivative(self, relative_predictions):
        return -self.step/relative_predictions**2

    def itrTrialDerivative(self, accuracy):
        return np.log2(accuracy * (self.n_targets - 1.0) / (1.0 - accuracy))

    def itrMinDerivativeAccuracy(self, accuracy, relative_predictions):
        return self.itrTrialDerivative(accuracy) * 60.0 / self.mdt(relative_predictions)

    def itrMinDerivativePredictions(self, accuracy, relative_predictions):
        return -self.mdtDerivative(relative_predictions)/self.mdt(relative_predictions)**2*self.itrBitPerTrial(accuracy)*60.0

    def itrMinDerivativePrecision(self, precisions, relative_predictions_per_class):
        accuracy = self.accuracy(precisions, relative_predictions_per_class)
        relative_predictions = self.relativePredictions(relative_predictions_per_class)
        return self.itrMinDerivativeAccuracy(accuracy, relative_predictions)*self.accuracyDerivativePrecision(relative_predictions_per_class)

    def itrMinDerivativePredictionsPerClass(self, precisions, relative_predictions_per_class):
        accuracy = self.accuracy(precisions, relative_predictions_per_class)
        relative_predictions = self.relativePredictions(relative_predictions_per_class)
        return self.itrMinDerivativeAccuracy(accuracy, relative_predictions)*self.accuracyDerivativePredictionsPerClass(precisions, relative_predictions_per_class) \
               + self.itrMinDerivativePredictions(accuracy, relative_predictions)*self.predictionsDerivative()

    def relativePredictions(self, relative_predictions_per_class):
        return sum(relative_predictions_per_class)

    def mdt(self, relative_predictions):
        return self.window_length + (self.look_back_length + self.feature_maf_length + self.proba_maf_length + 1.0/relative_predictions - 4)*self.step

    def itrFromPrecisionPredictions(self, precisions, relative_predictions_per_class):
        accuracy = self.accuracy(precisions, relative_predictions_per_class)
        relative_predictions = self.relativePredictions(relative_predictions_per_class)
        return self.itrBitPerMin(accuracy, relative_predictions)

    def itrBitPerMin(self, accuracy, relative_predictions):
        if relative_predictions == 0:
            return 0
        else:
            return self.itrBitPerTrial(accuracy)*60.0/self.mdt(relative_predictions)

    def itrBitPerTrial(self, accuracy):
        if self.n_targets == 1:
            return np.nan
        elif accuracy == 1:
            return np.log2(self.n_targets)
        elif accuracy == 0:
            return np.log2(self.n_targets)*np.log2(1.0/(self.n_targets-1))
        else:
            return np.log2(self.n_targets)+accuracy*np.log2(accuracy)+(1-accuracy)*np.log2((1.0-accuracy)/(self.n_targets-1))


class ItrAccuracySubMatrix(ItrCalculator):
    def accuracy(self, precisions, relative_predictions_per_class):
        return ItrCalculator.accuracy(self, precisions, relative_predictions_per_class)/self.relativePredictions(relative_predictions_per_class)

    def accuracyDerivativePrecision(self, relative_predictions_per_class):
        return ItrCalculator.accuracyDerivativePrecision(self, relative_predictions_per_class)/self.relativePredictions(relative_predictions_per_class)

    def accuracyDerivativePredictionsPerClass(self, precisions, relative_predictions_per_class):
        return ItrCalculator.accuracyDerivativePredictionsPerClass(self, precisions, relative_predictions_per_class)/self.relativePredictions(relative_predictions_per_class) \
            + ItrCalculator.accuracy(self, precisions, relative_predictions_per_class)*(-self.predictionsDerivative()/self.relativePredictions(relative_predictions_per_class)**2)


