import scipy
import scipy.interpolate
import numpy as np
import matplotlib2tikz
import matplotlib.pyplot as plt

from curves import Curve


class AverageCurve(object):
    def __init__(self, ordered_labels):
        self.curves = dict()
        self.ordered_labels = ordered_labels
        self.labels = None

    def addMacro(self):
        raise NotImplementedError("addMacro not implemented!")

    def addMicro(self, predictions, binary_labels):
        raise NotImplementedError("addMicro not implemented!")

    def getCurve(self, predictions):
        raise NotImplementedError("getCurve not implemented!")

    def setPlotLabels(self):
        raise NotImplementedError("setPlotLabels not implemented!")

    def getBinaryLabels(self, labels):
        binary_labels = []
        for label in self.ordered_labels:
            binary_labels.append(list(map(lambda x: x == label, labels)))
        return binary_labels

    def calculate(self, decision_function_values, labels):
        binary_labels = self.getBinaryLabels(labels)
        self.labels = np.transpose(binary_labels)
        self.calculateBinary(decision_function_values, binary_labels)
        self.addMicro(decision_function_values, binary_labels)
        self.addMacro()
        return self

    def calculateBinary(self, predictions, binary_labels):
        for i, label in enumerate(self.ordered_labels):
            curve = self.getCurve(predictions[i])
            curve.calculate(binary_labels[i], predictions[i])
            self.curves[label] = curve

    def getCurveLegendLabel(self, key):
        if isinstance(key, int):
            return 'Class {0}'.format(key)
        elif key in ["micro", "macro"]:
            return key + '-average'

    def plot(self, num=1):
        plt.figure(num)
        self.makePlot()
        # import time
        # matplotlib2tikz.save("C:\\Users\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\file" + str(round(time.time())) + ".tex")
        plt.draw()

    def makePlot(self):
        for key in sorted(self.curves):
            fpr, tpr, _, auc = self.curves[key].getValues()
            plt.plot(fpr, tpr, label=self.getCurveLegendLabel(key) + " (area = {0:0.2f})".format(auc))
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        self.setPlotLabels()
        plt.legend(loc="lower right")

    def calculateThresholds(self, *args):
        raise NotImplementedError("calculateThresholds not implemented!")

    def getClasses(self):
        return self.ordered_labels


class AverageRocCurve(AverageCurve):
    def addMacro(self):
        all_fpr = np.unique(np.concatenate([self.curves[label].x for label in self.ordered_labels]))
        mean_tpr = np.zeros_like(all_fpr)
        mean_threshold = np.zeros_like(all_fpr)
        for label in self.ordered_labels:
            x, y, thresholds, auc = self.curves[label].getValues()
            mean_tpr += scipy.interp(all_fpr, x, y)
            mean_threshold += scipy.interp(all_fpr, x, thresholds)
        mean_tpr /= len(self.ordered_labels)
        mean_threshold /= len(self.ordered_labels)
        curve = Curve.RocCurve(all_fpr, mean_tpr)
        curve.calculateAuc(all_fpr, mean_tpr)
        curve.thresholds = mean_threshold
        self.curves["macro"] = curve

    def addMicro(self, predictions, binary_labels):
        curve = Curve.RocCurve()
        curve.calculate(np.array(binary_labels).ravel(), predictions.ravel())
        self.curves["micro"] = curve

    def getCurve(self, predictions):
        return Curve.RocCurve(predictions=predictions)

    def setPlotLabels(self):
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC curve')

    # def calculateThresholds(self, class_count, fpr_threshold=0.05):
    #     for i in range(len(labels_order)):
    #         for j, (false_positive_rate, true_positive_rate, threshold) in enumerate(zip(fpr[i], tpr[i], thresholds[i])):
    #             if true_positive_rate == 1:
    #                 # assert j-1 > 0
    #                 cut_off_threshold.append(thresholds[i][j-1])
    #                 break
    #             if false_positive_rate > fpr_threshold:
    #                 cut_off_threshold.append(threshold)
    #                 break
    #         else:
    #             print "Warning: no cutoff obtained!"
    #     return cut_off_threshold


class AveragePrecisionRecallCurve(AverageCurve):
    def addMacro(self):
        all_fpr = np.unique(np.concatenate([self.curves[label].x for label in self.ordered_labels]))*-1
        mean_tpr = np.zeros_like(all_fpr)
        mean_threshold = np.zeros_like(all_fpr)
        for label in self.ordered_labels:
            x, y, thresholds, auc = self.curves[label].getValues()
            neg_x = x*-1
            neg_y = y*-1
            neg_thresholds = thresholds*-1
            mean_tpr += scipy.interp(all_fpr, neg_x, neg_y)
            mean_threshold += scipy.interp(all_fpr, neg_x[:-1], neg_thresholds)
        mean_tpr /= -len(self.ordered_labels)
        mean_threshold /= -len(self.ordered_labels)
        curve = Curve.PrecisionRecallCurve(list(reversed(all_fpr*-1)), list(reversed(mean_tpr)))
        # curve.calculateAuc(all_fpr, mean_tpr)
        curve.auc = -1
        curve.thresholds = list(reversed(mean_threshold))
        self.curves["macro"] = curve

    def addMicro(self, predictions, binary_labels):
        curve = Curve.PrecisionRecallCurve()
        curve.calculateCurve(np.array(binary_labels).ravel(), predictions.ravel())
        curve.calculateAuc(np.array(binary_labels), predictions, average="micro")
        self.curves["micro"] = curve

    def getCurve(self, predictions):
        return Curve.PrecisionRecallCurve(predictions=predictions)

    def setPlotLabels(self):
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-recall curve')

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

    def throwToMiddle(self, length):
        return int(np.ceil((length-1)*np.random.rand()))

    def getData(self, all_data, indices):
        return map(lambda (x, i): x[i], zip(all_data, indices))

    # def calculateNewIndices(self, itr_change, indices, lengths, step):
    #     new_indices = []
    #     for index, change, length in zip(indices, itr_change, lengths):
    #         new_value = index+int(np.round(change*step))
    #         # new_value = index+int(np.sign(change*step)*np.ceil(np.abs(change*step)))
    #         if 0 < new_value < length-1:
    #             new_indices.append(new_value)
    #         else:
    #             new_indices.append(np.random.randint(0, length))
    #     return new_indices

    def calculateNewThresholds(self, itr_change, current_thresholds, mins, maxs, mu):
        new_thresholds = []
        for threshold, change, min, max in zip(current_thresholds, itr_change, mins, maxs):
            new_threshold = threshold+change*mu
            # new_threshold = threshold+int(np.sign(change*step)*np.ceil(np.abs(change*step)))
            if min <= new_threshold <= max:
                new_thresholds.append(new_threshold)
            else:
                new_thresholds.append(max)
        return new_thresholds

    def randBetween(self, min, max):
        return np.random.rand()*(max-min)+min

    def makeFunction(self, coefficients):
        return lambda x: sum(p*x**(len(coefficients)-1-i) for i, p in enumerate(coefficients))

    def makeDerivative(self, coefficient):
        return lambda x: sum(p*x**(len(coefficient[:-1])-1-i)*(len(coefficient)-1-i) for i, p in enumerate(coefficient[:-1]))

    def gradientDescent(self, starting_mu, current_thresholds, precision_functions, prediction_functions, precision_derivative, prediction_derivative, all_thresholds, all_precisions, all_relative_predictions, all_predictions, itr_calculator, min_thresholds, max_thresholds, n_predictions):
        previous_itr = None
        max_itr = None
        max_itr_indices = None
        # previous_thresholds = []
        mu = starting_mu*10
        for i in range(50):
            mu /= 10
            for i in range(500):
                indices = [thresholds.searchsorted(threshold, side="left") for threshold, thresholds in zip(current_thresholds, all_thresholds)]

                precision = [np.asscalar(func(threshold)) for func, threshold in zip(precision_functions, current_thresholds)]
                relative_predictions = [np.asscalar(func(threshold)) for func, threshold in zip(prediction_functions, current_thresholds)]
                current_dp = [np.asscalar(func(threshold)) for func, threshold in zip(precision_derivative, current_thresholds)]
                current_dr = [np.asscalar(func(threshold)) for func, threshold in zip(prediction_derivative, current_thresholds)]
                precision = [np.min((p, 1.0)) for p in precision]
                relative_predictions = [np.max((r, 0)) for r in relative_predictions]

                # actual_precision = [p[i] for p, i in zip(all_precisions, indices)]
                # actual_predictions = [p[i] for p, i in zip(all_relative_predictions, indices)]
                current_itr = itr_calculator.itrFromPrecisionPredictions(precision, relative_predictions)
                # itr_closest = itr_calculator.itrFromPrecisionPredictions(actual_precision, actual_predictions)
                # if True:  # fixing ITR, only works for 3 targets
                #     over_threshold = np.transpose([np.array(pred) > thresh for pred, thresh in zip(all_predictions, current_thresholds)])
                #     counts = over_threshold.sum(1)
                #     sum_1 = np.where(counts == 1)
                #     prediction_count = float(sum_1[0].shape[0])
                #     accuracy = np.logical_and(self.labels[sum_1, :], over_threshold[sum_1, :]).sum()/prediction_count
                #     predictions = prediction_count/float(n_predictions)
                #     actual_itr = itr_calculator.itrBitPerMin(accuracy, predictions)
                #     if np.isnan(actual_itr) or np.isnan(current_itr):
                #         print "encountered nan!", actual_itr, current_itr#, precision, relative_predictions, current_dp, current_dr
                #     if np.isnan(actual_itr):
                #         actual_itr = current_itr
                if np.isnan(current_itr):
                    print "encountered nan!", current_itr
                if max_itr is None or current_itr > max_itr:
                    max_itr = current_itr
                    max_itr_indices = indices
                itr_change = itr_calculator.derivative(precision, relative_predictions, current_dp, current_dr)
                # print current_itr, itr_closest, actual_itr
                # print precision, relative_predictions, itr_change
                current_thresholds = self.calculateNewThresholds(itr_change, current_thresholds, min_thresholds, max_thresholds, mu)
                # raw_input()
                if previous_itr is not None and abs(current_itr-previous_itr) < 0.000001:# or current_thresholds in previous_thresholds:
                    # print "Done"
                    # print [thresh[index] for thresh, index in zip(all_thresholds, max_itr_indices)]
                    return max_itr, max_itr_indices
                # previous_thresholds.append(current_thresholds)
                previous_itr = current_itr
            print "Decreasing mu!"
        print "Max iter exceeded!"
        # print [thresh[index] for thresh, index in zip(all_thresholds, max_itr_indices)]
        return max_itr, max_itr_indices

    def extendThresholdsValues(self, thresholds):
        min = thresholds[0]
        max = thresholds[-1]
        range = (max-min)*0.2
        return [min-range, max+range]

    def extendThresholds(self, all_thresholds):
        return [np.insert(thresholds, [0, len(thresholds)-1], self.extendThresholdsValues(thresholds)) for thresholds in all_thresholds]

    def extendYValuesHelper(self, values):
        first = values[0]
        last = values[-1]
        return [first, last]

    def extendYValues(self, y_values):
        return [np.insert(values, [0, len(values)-1], self.extendYValuesHelper(values)) for values in y_values]

    def fitCurves(self, thresholds, precisions, predictions):
        precision_coefficients = [
            np.polyfit(threshold, precision, deg=7)
            for threshold, precision in zip(thresholds, precisions)
        ]
        prediction_coefficients = [
            np.polyfit(threshold, relative_prediction, deg=7)
            for threshold, relative_prediction in zip(thresholds, predictions)
        ]
        precision_functions = [
            self.makeFunction(coefficient)
            for coefficient in precision_coefficients
        ]
        prediction_functions = [
            self.makeFunction(coefficient)
            for coefficient in prediction_coefficients
        ]
        precision_derivative = [
            self.makeDerivative(coefficient)
            for coefficient in precision_coefficients
        ]
        prediction_derivative = [
            self.makeDerivative(coefficient)
            for coefficient in prediction_coefficients
        ]
        return precision_functions, prediction_functions, precision_derivative, prediction_derivative

    def plotCurves(self, thresholds, precisions, precision_function, predictions, prediction_function, precision_derivative, prediction_derivative):
        points = np.linspace(thresholds[0], thresholds[-1], 3000)
        plt.figure()
        plt.ylim(0, 1.1)
        plt.plot(thresholds, precisions)
        plt.plot(points, precision_function(points))
        plt.figure()
        plt.plot(thresholds, predictions)
        plt.plot(points, prediction_function(points))
        plt.figure()
        plt.plot(points, precision_derivative(points))
        plt.plot(points, prediction_derivative(points))

    def calculatePrecisionPredictionCurves(self, all_thresholds, all_precisions, all_relative_predictions):
        extended_thresholds = self.extendThresholds(all_thresholds)
        extended_precisions = self.extendYValues(all_precisions)
        extended_prediction = self.extendYValues(all_relative_predictions)
        precision_functions, prediction_functions, precision_derivative, prediction_derivative = self.fitCurves(extended_thresholds, extended_precisions, extended_prediction)
        # precision_functions1, prediction_functions1, precision_derivative1, prediction_derivative1 = self.fitCurves(all_thresholds, all_precisions, all_relative_predictions)
        # class_index = 0
        # self.plotCurves(all_thresholds[class_index], all_precisions[class_index], precision_functions[class_index], all_relative_predictions[class_index], prediction_functions[class_index], precision_derivative[class_index], prediction_derivative[class_index])
        # self.plotCurves(all_thresholds[class_index], all_precisions[class_index], precision_functions1[class_index], all_relative_predictions[class_index], prediction_functions1[class_index], precision_derivative1[class_index], prediction_derivative1[class_index])
        # plt.show()
        return precision_functions, prediction_functions, precision_derivative, prediction_derivative

    def calculateThresholds(self, itr_calculator, itr_calculator2):
        all_precisions = []  # Threshold with derivatives ITR
        all_relative_predictions = []
        all_thresholds = []
        lengths = []
        max_thresholds = []
        min_thresholds = []
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
            max_thresholds.append(thresholds[-1])
            min_thresholds.append(thresholds[0])
            # plt.ylim(0, 1.1)
            # plt.plot(thresholds, precisions[:-1])
            # plt.plot(thresholds, relative_predictions)
            # plt.show()
        all_predictions = np.array(all_predictions)
        # itrs = []
        # for p1, r1 in zip(all_precisions[0], all_relative_predictions[0]):
        #     for p2, r2 in zip(all_precisions[1], all_relative_predictions[1]):
        #         for p3, r3 in zip(all_precisions[2], all_relative_predictions[2]):
        #             itrs.append(itr_calculator.itrFromPrecisionPredictions([p1,p2,p3], [r1,r2,r3])) # 58.3526461033  15482509
        # print max(itrs)
        # print np.argmax(itrs)
        precision_functions, prediction_functions, precision_derivative, prediction_derivative = self.calculatePrecisionPredictionCurves(all_thresholds, all_precisions, all_relative_predictions)
        max_itrs = []
        max_itrs_indices = []
        import time
        start_time = time.time()
        for k in range(4):
            if k == 0:
                current_thresholds = self.calculateThresholdsMaxPrecision()
            elif k == 1:
                current_thresholds = self.calculateThresholdsMaxItrSingle(itr_calculator.itrBitPerMin)
            else:
                indices = map(lambda x: np.random.randint(0, x), lengths)
                current_thresholds = map(lambda (x,y): x[y], zip(all_thresholds, indices))
            starting_mu = 0.00001
            itr, indices = self.gradientDescent(
                starting_mu,
                current_thresholds,
                precision_functions,
                prediction_functions,
                precision_derivative,
                prediction_derivative,
                all_thresholds,
                all_precisions,
                all_relative_predictions,
                all_predictions,
                itr_calculator,
                min_thresholds,
                max_thresholds,
                n_prediction
            )
            max_itrs.append(itr)
            max_itrs_indices.append(indices)
        print time.time()- start_time
        raw_input()
        # print max_itrs
        return [thresh[index] for thresh, index in zip(all_thresholds, max_itrs_indices[np.argmax(max_itrs)])]
