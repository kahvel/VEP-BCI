import numpy as np
import scipy.optimize


class Optimiser(object):
    def __init__(self, itr_calculator):
        self.ordered_labels = None
        self.curves = None
        self.labels = None
        self.itr_calculator = itr_calculator

    def setCurveData(self, ordered_labels, curves, labels):
        self.ordered_labels = ordered_labels
        self.curves = curves
        self.labels = labels

    def calculateThresholdsMaxPrecision(self):
        # threshold_indices = []
        cut_off_threshold = []
        for key in self.ordered_labels:
            _, y, thresholds, _ = self.curves[key].getValues()
            index = np.argmax(y[:-1])
            # threshold_indices.append(index)
            cut_off_threshold.append(thresholds[index])
        return cut_off_threshold

    def calculateThresholdsMaxItrSingle(self, optimisation_function):
        # threshold_indices = []
        cut_off_threshold = []
        for key in self.ordered_labels:
            x, y, thresholds, _ = self.curves[key].getValues()
            itrs = map(lambda (r, p): optimisation_function(p, r), zip(x, y))
            index = np.argmax(itrs[:-1])
            # threshold_indices.append(index)
            cut_off_threshold.append(thresholds[index])
        return cut_off_threshold

    def makeInitialGuess(self, k, all_thresholds, lengths):
        if k == 0:
            return self.calculateThresholdsMaxPrecision()
        elif k == 1:
            return self.calculateThresholdsMaxItrSingle(self.itr_calculator.itrBitPerMin)
        elif k == 2:
            return map(lambda x: x[-1], all_thresholds)
        else:
            indices = map(lambda x: np.random.randint(0, x), lengths)
            return map(lambda (x,y): x[y], zip(all_thresholds, indices))

    def findOptimalThresholds(self, function, initial_guess, bounds, gradient, constraints):
        raise NotImplementedError("findOptimalThresholds not implemented!")

    def fitCurves(self, all_thresholds, all_precisions, all_relative_predictions, all_predictions, labels):
        raise NotImplementedError("fitCurves not implemented!")

    def _optimise(self, function, gradient, constraints):
        all_precisions = []
        all_relative_predictions = []
        all_thresholds = []
        lengths = []
        bounds = []
        all_predictions = []
        for key in self.ordered_labels:
            _, precisions, thresholds, _ = self.curves[key].getValues()
            predictions = self.curves[key].getPredictions()
            n_prediction = len(predictions)
            all_predictions.append(predictions)
            relative_predictions = (n_prediction + 1.0 - np.sort(predictions).searchsorted(thresholds, side="right"))/n_prediction
            all_precisions.append(precisions[:-1])
            all_relative_predictions.append(relative_predictions)
            all_thresholds.append(thresholds)
            lengths.append(len(thresholds))
            bounds.append((thresholds[0], thresholds[-1]))
        all_predictions = np.array(all_predictions)
        # itrs = []
        # for p1, r1 in zip(all_precisions[0], all_relative_predictions[0]):
        #     for p2, r2 in zip(all_precisions[1], all_relative_predictions[1]):
        #         for p3, r3 in zip(all_precisions[2], all_relative_predictions[2]):
        #             itrs.append(itr_calculator.itrFromPrecisionPredictions([p1,p2,p3], [r1,r2,r3])) # 58.3526461033  15482509
        # print max(itrs)
        # print np.argmax(itrs)
        self.fitCurves(all_thresholds, all_precisions, all_relative_predictions, all_predictions, self.labels)

        max_itrs = []
        max_itr_thresholds = []
        for k in range(5):
            initial_guess = self.makeInitialGuess(k, all_thresholds, lengths)
            thresholds, itr = self.findOptimalThresholds(function, initial_guess, bounds, gradient, constraints)
            max_itrs.append(itr)
            max_itr_thresholds.append(thresholds)
            # print np.array(thresholds), itr
        result = max_itr_thresholds[np.argmax(max_itrs)]
        return result
        # indices = [thresholds.searchsorted(threshold, side="left") for threshold, thresholds in zip(result, all_thresholds)]
        # indices = map(lambda (len, i): i if i < len else len-1, zip(lengths, indices))
        # return [thresh[index] for thresh, index in zip(all_thresholds, indices)]


class SequentialLeastSquaresProgrammingActual(Optimiser):
    def fitCurves(self, all_thresholds, all_precisions, all_relative_predictions, all_predictions, labels):
        self.itr_calculator.setValues(all_thresholds, all_precisions, all_relative_predictions, all_predictions, labels)

    def findOptimalThresholds(self, function, initial_guess, bounds, gradient, constraints):
        result = scipy.optimize.minimize(
            lambda x: -function(x),
            initial_guess,
            method="SLSQP",
            # jac=itr_calculator.gradient,
            bounds=bounds,
            constraints=constraints,
            # options={"disp": True}
        )
        return result.x, result.fun

    def optimise(self):
        return self._optimise(
            self.itr_calculator.actualItr,
            None,
            (),
        )


class SequentialLeastSquaresProgrammingSimplified(Optimiser):
    def fitCurves(self, all_thresholds, all_precisions, all_relative_predictions, all_predictions, labels):
        self.itr_calculator.fitCurves(all_thresholds, all_precisions, all_relative_predictions, all_predictions, labels)

    def callback(self, current_thresholds):
        print "debug", current_thresholds, self.itr_calculator.itrFromThresholds(current_thresholds)

    def findOptimalThresholds(self, function, initial_guess, bounds, gradient, constraints):
        result = scipy.optimize.minimize(
            lambda x: -function(x),
            initial_guess,
            method="SLSQP",
            jac=gradient,
            bounds=bounds,
            constraints=constraints,
            # options={"disp": True},
            # callback=self.callback,
        )
        return result.x, result.fun

    def optimise(self):
        return self._optimise(
            self.itr_calculator.itrFromThresholds,
            self.itr_calculator.gradient,
            (),
            # [
            #     {"type": "ineq", "fun": self.itr_calculator.accuracyUpperBound},
            #     {"type": "ineq", "fun": self.itr_calculator.accuracyLowerBound},
            #     {"type": "ineq", "fun": self.itr_calculator.predictionsUpperBound},
            #     {"type": "ineq", "fun": self.itr_calculator.predictionsLowerBound},
            # ]
        )


class GradientDescentOptimiser(Optimiser):
    def fitCurves(self, all_thresholds, all_precisions, all_relative_predictions, all_predictions, labels):
        self.itr_calculator.fitCurves(all_thresholds, all_precisions, all_relative_predictions, all_predictions, labels)

    def optimise(self):
        return self._optimise(
            self.itr_calculator.itrFromThresholds,
            self.itr_calculator.gradient,
            None,
        )

    def calculateNewThresholds(self, itr_change, current_thresholds, bounds, mu):
        new_thresholds = []
        for threshold, change, bound in zip(current_thresholds, itr_change, bounds):
            new_threshold = threshold+change*mu
            # new_threshold = threshold+int(np.sign(change*step)*np.ceil(np.abs(change*step)))
            if bound[0] <= new_threshold <= bound[1]:
                new_thresholds.append(new_threshold)
            elif new_threshold > bound[1]:
                new_thresholds.append(bound[1])
            else:
                new_thresholds.append(bound[0])
        return new_thresholds

    def findOptimalThresholds(self, function, initial_guess, bounds, gradient, constraints):
        previous_itr = None
        max_itr = None
        max_thresholds1 = None
        # previous_thresholds = []
        mu = 0.0001
        stop_threshold = 0.000001
        steps_before_decreasing = 100
        n_decreases = 50
        current_thresholds = initial_guess
        for j in range(n_decreases):
            mu /= 2
            # stop_threshold /= 10
            for i in range(steps_before_decreasing):
                current_itr = function(current_thresholds)
                if max_itr is None or current_itr > max_itr:
                    max_itr = current_itr
                    max_thresholds1 = current_thresholds
                itr_change = gradient(current_thresholds)
                current_thresholds = self.calculateNewThresholds(itr_change, current_thresholds, bounds, mu)
                if previous_itr is not None and abs(current_itr-previous_itr) < stop_threshold:# or current_thresholds in previous_thresholds:
                    # print max_actual, max_itr, max_itr_indices, max_actual_indices, "kartul", np.sum(np.array(max_itr_indices) == np.array(max_actual_indices))
                    print "Converged in", j*steps_before_decreasing+i, "steps. Mu:", mu
                    # print [thresh[index] for thresh, index in zip(all_thresholds, max_itr_indices)]
                    return max_thresholds1, max_itr
                # previous_thresholds.append(current_thresholds)
                previous_itr = current_itr
            # print "Decreasing mu!"
        print "Max iter exceeded!"
        # print [thresh[index] for thresh, index in zip(all_thresholds, max_itr_indices)]
        return max_thresholds1, max_itr
