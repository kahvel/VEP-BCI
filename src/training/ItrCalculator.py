import numpy as np

from training.curve_fitting import Polynomial, SumSkewNormal


class ItrCalculator(object):
    def __init__(self, window_length, step, feature_maf_length, proba_maf_length, look_back_length, n_targets, precisions_bounded, predictions_bounded):
        self.window_length = window_length
        self.step = step
        self.feature_maf_length = feature_maf_length
        self.proba_maf_length = proba_maf_length
        self.look_back_length = look_back_length
        self.n_targets = n_targets
        self.precision_curve_fitting = Polynomial.PrecisionCurveFitter()
        self.prediction_curve_fitting = Polynomial.PredictionCurveFitter()
        self.precisions_bounded = precisions_bounded
        self.predictions_bounded = predictions_bounded
        self.all_thresholds = None
        self.all_precisions = None
        self.all_predictions = None
        self.all_predicted_scores = None
        self.labels = None
        self.n_samples = None
        self.precision_handler = None
        self.predictions_handler = None

    def fitCurves(self, all_thresholds, all_precisions, all_relative_predictions, all_predicted_scores, labels):
        self.setValues(all_thresholds, all_precisions, all_relative_predictions, all_predicted_scores, labels)
        self.calculateCurves(all_thresholds, all_precisions, all_relative_predictions, all_predicted_scores, labels)

    def calculateCurves(self, all_thresholds, all_precisions, all_relative_predictions, all_predicted_scores, labels):
        precision_functions, precision_derivatives = self.precision_curve_fitting.fitCurves(all_thresholds, all_precisions)
        prediction_functions, prediction_derivatives = self.prediction_curve_fitting.fitCurves(all_thresholds, all_relative_predictions)
        self.precision_handler = ValuesHandlerPrecisionOrPrediction(self.all_precisions, self.precisions_bounded, precision_functions, precision_derivatives)
        self.predictions_handler = ValuesHandlerPrecisionOrPrediction(self.all_predictions, self.predictions_bounded, prediction_functions, prediction_derivatives)

    def setValues(self, all_thresholds, all_precisions, all_relative_predictions, all_predicted_scores, labels):
        self.all_thresholds = all_thresholds
        self.all_precisions = all_precisions
        self.all_predictions = all_relative_predictions
        self.all_predicted_scores = all_predicted_scores
        self.labels = labels
        self.n_samples = len(self.all_predicted_scores[0])

    def gradient(self, thresholds):
        p = self.precision_handler.getValueAt(thresholds)
        i = self.predictions_handler.getValueAt(thresholds)
        dp_dt = self.precision_handler.getDerivativeValueAt(thresholds)
        di_dt = self.predictions_handler.getDerivativeValueAt(thresholds)
        return self.derivative(p, i, dp_dt, di_dt)

    def derivative(self, p, i, dp_dt, di_dt):
        return dp_dt*self.dITR_dp(p, i) + di_dt*self.dITR_di(p, i)

    def accuracy(self, p, i):
        return sum(map(lambda (p, i): p*i, zip(p, i)))

    def da_dp(self, i):
        return np.array(i)

    def da_di(self, p, i):
        return np.array(p)

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
            return np.log2(self.n_targets)*np.log2(1.0/(self.n_targets-1))
        else:
            return np.log2(self.n_targets)+a*np.log2(a)+(1-a)*np.log2((1.0-a)/(self.n_targets-1))

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


class ItrAccuracySubMatrix(ItrCalculator):
    def accuracy(self, p, i):
        return ItrCalculator.accuracy(self, p, i)/self.relativePredictions(i)

    def da_dp(self, i):
        return ItrCalculator.da_dp(self, i)/self.relativePredictions(i)

    def da_di(self, p, i):
        return ItrCalculator.da_di(self, p, i)/self.relativePredictions(i) \
            + ItrCalculator.accuracy(self, p, i)*(-self.dr_di()/self.relativePredictions(i)**2)


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


class ValuesHandlerPrecisionOrPrediction(ValuesHandler):
    def __init__(self, values, use_bounds, fit_curves, fit_curve_derivative):
        ValuesHandler.__init__(self, values, fit_curves, fit_curve_derivative)
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


class ProbValuesHandler(ValuesHandler):
    def getValueAt(self, xs):
        return 1-self.getValueFromCurve(self.fit_curves, xs)

    def getDerivativeValueAt(self, xs):
        return -self.getValueFromCurve(self.fit_curve_derivative, xs)


class ItrCalculatorProb(ItrAccuracySubMatrix):
    def __init__(self, window_length, step, feature_maf_length, proba_maf_length, look_back_length, n_targets, precisions_bounded, predictions_bounded):
        ItrAccuracySubMatrix.__init__(self, window_length, step, feature_maf_length, proba_maf_length, look_back_length, n_targets, precisions_bounded, predictions_bounded)
        self.prob_curve_fitting = SumSkewNormal.DistrubutionSumCurves()
        self.prob_value_handler = None

    def calculateCurves(self, all_thresholds, all_precisions, all_relative_predictions, all_predicted_scores, labels):
        self.prob_curve_fitting.fitCurves(all_predicted_scores, labels)
        # functions, derivatives = self.prob_curve_fitting.fitCurves(all_predicted_scores, labels)
        # self.prob_value_handler = ProbValuesHandler(None, functions, derivatives)

    def itrFromThresholds(self, thresholds):
        return sum(thresholds)/100000

    def gradient(self, thresholds):
        return thresholds
