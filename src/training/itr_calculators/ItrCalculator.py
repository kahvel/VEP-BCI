import numpy as np

from training.curve_fitting import Polynomial
from training.itr_calculators import AbstractCalculator


class ItrCalculator(AbstractCalculator.ItrCalculator):
    def __init__(self, window_length, step, feature_maf_length, proba_maf_length, look_back_length, n_targets, precisions_bounded, predictions_bounded):
        AbstractCalculator.ItrCalculator.__init__(self, window_length, step, feature_maf_length, proba_maf_length, look_back_length, n_targets)
        self.precision_curve_fitting = Polynomial.PrecisionCurveFitter()
        self.prediction_curve_fitting = Polynomial.PredictionCurveFitter()
        self.precisions_bounded = precisions_bounded
        self.predictions_bounded = predictions_bounded
        self.all_thresholds = None
        self.all_precisions = None
        self.all_predictions = None
        self.precision_handler = None
        self.predictions_handler = None

    def fitCurves(self, all_predicted_scores, labels, all_thresholds, all_precisions, all_relative_predictions):
        self.setValues(all_predicted_scores, labels, all_thresholds, all_precisions, all_relative_predictions)
        self.calculateCurves(all_thresholds, all_precisions, all_relative_predictions)

    def calculateCurves(self, all_thresholds, all_precisions, all_relative_predictions):
        precision_functions, precision_derivatives = self.precision_curve_fitting.fitCurves(all_thresholds, all_precisions)
        prediction_functions, prediction_derivatives = self.prediction_curve_fitting.fitCurves(all_thresholds, all_relative_predictions)
        self.precision_handler = ValuesHandlerPrecisionOrPrediction(self.all_precisions, self.precisions_bounded, precision_functions, precision_derivatives)
        self.predictions_handler = ValuesHandlerPrecisionOrPrediction(self.all_predictions, self.predictions_bounded, prediction_functions, prediction_derivatives)

    def setValues(self, all_predicted_scores, labels, all_thresholds=None, all_precisions=None, all_relative_predictions=None):
        ItrCalculator.setValues(self, all_predicted_scores, labels)
        self.all_thresholds = all_thresholds
        self.all_precisions = all_precisions
        self.all_predictions = all_relative_predictions

    def gradient(self, thresholds):
        p = self.precision_handler.getValueAt(thresholds)
        i = self.predictions_handler.getValueAt(thresholds)
        dp_dt = self.precision_handler.getDerivativeValueAt(thresholds)
        di_dt = self.predictions_handler.getDerivativeValueAt(thresholds)
        return self.derivative(p, i, dp_dt, di_dt)

    def derivative(self, p, i, dp_dt, di_dt):
        return dp_dt*self.dITR_dp(p, i) + di_dt*self.dITR_di(p, i)

    def accuracyFromWholeMatrix(self, p, i):  # Including the "nothing" class
        return sum(map(lambda (p, i): p*i, zip(p, i)))

    def da_dp_whole_matrix(self, i):
        return np.array(i)

    def da_di_whole_matrix(self,p, i):
        return np.array(p)

    def accuracy(self, p, i):
        raise NotImplementedError("accuracy is not implemented!")

    def da_dp(self, i):
        raise NotImplementedError("da_dp not implemented!")

    def da_di(self, p, i):
        raise NotImplementedError("da_di not implemented!")

    def dr_di(self):
        return np.ones(self.n_targets)

    def dMDT_dr(self, r):
        return -self.step/r**2

    def dITRt_da(self, a):
        if a == 1.0:
            return 0
        else:
            return np.log2(a * (self.n_targets - 1.0) / (1.0 - a))

    def dITR_da(self, a, r):
        return self.dITRt_da(a) * 60.0 / self.mdt(r)

    def dITR_dr(self, a, r):
        return -self.dMDT_dr(r)/self.mdt(r)**2*self.itrBitPerTrial(a)*60.0

    def dITR_dp(self, p, i):
        a = self.accuracy(p, i)
        r = self.relativePredictions(i)
        return self.dITR_da(a, r)*self.da_dp(i)

    def dITR_di(self, p, i):
        a = self.accuracy(p, i)
        r = self.relativePredictions(i)
        return self.dITR_da(a, r)*self.da_di(p, i) + self.dITR_dr(a, r)*self.dr_di()

    def relativePredictions(self, relative_predictions_per_class):
        return sum(relative_predictions_per_class)

    def mdt(self, r):
        return self.window_length + (self.look_back_length + self.feature_maf_length + self.proba_maf_length + 1.0/r - 4)*self.step

    def itrFromPrecisionPredictions(self, p, i):
        a = self.accuracy(p, i)
        r = self.relativePredictions(i)
        return self.itrBitPerMin(a, r)

    def itrFromThresholds(self, thresholds):
        p = self.precision_handler.getValueAt(thresholds)
        i = self.predictions_handler.getValueAt(thresholds)
        result = self.itrFromPrecisionPredictions(p, i)
        if np.isnan(result):
            print "encountered nan!", p, i, thresholds
        return result

    def getIndicesClosestToThresholds(self, current_thresholds, indices):
        if indices is None:
            return [thresholds.searchsorted(threshold, side="left") for threshold, thresholds in zip(current_thresholds, self.all_thresholds)]
        else:  # Already have indices
            return indices

    def itrFromThresholdsClosestToUnfitValues(self, current_thresholds, indices=None):
        indices_in_initial_matrix = self.getIndicesClosestToThresholds(current_thresholds, indices)
        p = self.precision_handler.getClosestUnfitValue(indices_in_initial_matrix)
        i = self.predictions_handler.getClosestUnfitValue(indices_in_initial_matrix)
        return self.itrFromPrecisionPredictions(p, i)

    def accuracyUpperBound(self, thresholds):
        p = self.precision_handler.getValueAt(thresholds)
        i = self.predictions_handler.getValueAt(thresholds)
        return self.accuracy(p, i)

    def accuracyLowerBound(self, thresholds):
        p = self.precision_handler.getValueAt(thresholds)
        i = self.predictions_handler.getValueAt(thresholds)
        return 1 - self.accuracy(p, i)

    def predictionsUpperBound(self, thresholds):
        i = self.predictions_handler.getValueAt(thresholds)
        return self.relativePredictions(i)

    def predictionsLowerBound(self, thresholds):
        i = self.predictions_handler.getValueAt(thresholds)
        return 1 - self.relativePredictions(i)


class ItrAccuracyWholeMatrix(ItrCalculator):
    def accuracy(self, p, i):
        return self.accuracyFromWholeMatrix(p, i)

    def da_dp(self, i):
        return self.da_dp_whole_matrix(i)

    def da_di(self, p, i):
        return self.da_di_whole_matrix(p, i)


class ItrAccuracySubMatrix(ItrCalculator):
    def accuracy(self, p, i):
        return self.accuracyFromWholeMatrix(p, i)/self.relativePredictions(i)

    def da_dp(self, i):
        return self.da_dp_whole_matrix(i)/self.relativePredictions(i)

    def da_di(self, p, i):
        return self.da_di_whole_matrix(p, i)/self.relativePredictions(i) \
            + self.accuracyFromWholeMatrix(p, i)*(-self.dr_di()/self.relativePredictions(i)**2)


class ValuesHandlerPrecisionOrPrediction(AbstractCalculator.ValuesHandler):
    def __init__(self, values, use_bounds, fit_curves, fit_curve_derivative):
        AbstractCalculator.ValuesHandler.__init__(self, values, fit_curves, fit_curve_derivative)
        self.use_bounds = use_bounds

    def getBoundedBetween(self, values, upper_bound=1.0, lower_bound=0.0):
        return [np.max((np.min((p, upper_bound)), lower_bound)) for p in values]

    def useBoundsOnValues(self, values):
        if self.use_bounds:
            return self.getBoundedBetween(values)
        else:
            return values

    def getValueAt(self, thresholds):
        return self.getValueAtBounded(thresholds)

    def getValueAtUnbounded(self, thresholds):
        return self.getValueFromCurve(self.fit_curves, thresholds)

    def getValueAtBounded(self, thresholds):
        return self.useBoundsOnValues(self.getValueFromCurve(self.fit_curves, thresholds))

    def getDerivativeValueAt(self, thresholds):
        return self.getValueFromCurve(self.fit_curve_derivative, thresholds)

    def getClosestUnfitValue(self, indices):
        return [v[i] for v, i in zip(self.values, indices)]
