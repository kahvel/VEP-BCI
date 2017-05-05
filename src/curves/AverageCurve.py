import scipy
import numpy as np
import matplotlib2tikz
import matplotlib.pyplot as plt

from curves import Curve


class AverageCurve(object):
    def __init__(self, ordered_labels):
        self.curves = dict()
        self.ordered_labels = ordered_labels

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
        threshold_indices = []
        # cut_off_threshold = []
        for key in self.ordered_labels:
            _, y, thresholds, _ = self.curves[key].getValues()
            index = np.argmax(y[:-1])
            threshold_indices.append(index)
            # cut_off_threshold.append(thresholds[index])
        return threshold_indices

    def calculateThresholdsMaxItrSingle(self, optimisation_function):
        threshold_indices = []
        # cut_off_threshold = []
        for key in self.ordered_labels:
            x, y, thresholds, _ = self.curves[key].getValues()
            itrs = map(lambda (r, p): optimisation_function(p, r), zip(x, y))
            index = np.argmax(itrs[:-1])
            threshold_indices.append(index)
            # cut_off_threshold.append(thresholds[index])
        return threshold_indices

    def throwToMiddle(self, length):
        return int(np.ceil((length-1)*np.random.rand()))

    def getData(self, all_data, indices):
        return map(lambda (x, i): x[i], zip(all_data, indices))

    def calculateNewIndices(self, itr_change, indices, lengths, step):
        new_indices = []
        for index, change, length in zip(itr_change, indices, lengths):
            new_value = index+int(np.round(change*step))
            # new_value = index+int(np.sign(change*step)*np.ceil(np.abs(change*step)))
            if 0 < new_value < length-1:
                new_indices.append(new_value)
            else:
                new_indices.append(np.random.randint(0, length))
        return new_indices

    def calculateThresholds(self, itr_calculator, itr_calculator2):
        all_precisions = []  # Threshold with derivatives ITR
        all_relative_predictions = []
        all_thresholds = []
        lengths = []
        for key in self.ordered_labels:
            _, precisions, thresholds, _ = self.curves[key].getValues()
            predictions = self.curves[key].getPredictions()
            n_predictions = len(predictions)
            relative_predictions = (n_predictions + 1.0 - np.sort(sorted(predictions)).searchsorted(thresholds, side="right"))/n_predictions
            all_precisions.append(precisions[:-1])
            all_relative_predictions.append(relative_predictions)
            all_thresholds.append(thresholds)
            lengths.append(len(thresholds))
        # itrs = []
        # for p1, r1 in zip(all_precisions[0], all_relative_predictions[0]):
        #     for p2, r2 in zip(all_precisions[1], all_relative_predictions[1]):
        #         for p3, r3 in zip(all_precisions[2], all_relative_predictions[2]):
        #             itrs.append(itr_calculator.itrFromPrecisionPredictions([p1,p2,p3], [r1,r2,r3])) # 58.3526461033  15482509
        # print max(itrs)
        # print np.argmax(itrs)
        # raw_input()
        # dp = map(lambda x: np.insert(np.diff(x), len(x)-1, np.nan), all_precisions)
        # dr = map(lambda x: np.insert(np.diff(x), len(x)-1, np.nan), all_relative_predictions)
        all_data = [np.transpose((all_precisions[i], all_relative_predictions[i], all_thresholds[i])) for i in range(len(self.ordered_labels))]
        for k in range(4):
            # indices = [0 for _ in self.ordered_labels]
            if k == 0:
                indices = self.calculateThresholdsMaxPrecision()
            elif k == 1:
                indices = self.calculateThresholdsMaxItrSingle(itr_calculator.itrBitPerMin)
            elif k >= 2:
                indices = map(lambda x: np.random.randint(0, x), lengths)
            # indices = self.calculateThresholdsMaxItrSingle(itr_calculator2.itrBitPerMin)
            step = 21
            step_decrease = 4
            for i in range(step-1):
                previous_points = []
                itrs = []
                # print indices
                while True:
                    current_data = self.getData(all_data, indices)
                    [precision, relative_predictions, thresholds] = np.transpose(current_data)
                    no_difference = [j+1 >= length for j, length in zip(indices, lengths)]
                    if any(no_difference):
                        # print "Reached end of array! Cannot calculate derivative"
                        for j, no in enumerate(no_difference):
                            if no:
                                indices[j] = self.throwToMiddle(lengths[j])
                        continue
                    data_step_away = self.getData(all_data, map(lambda x: x+1, indices))
                    [precision1, relative_predictions1, thresholds1] = np.transpose(data_step_away)
                    dp = precision1-precision
                    dr = relative_predictions1-relative_predictions
                    current_itr = itr_calculator.itrFromPrecisionPredictions(precision, relative_predictions)
                    itrs.append(current_itr)
                    previous_points.append(indices[:])
                    itr_change = itr_calculator.derivative(precision, relative_predictions, dp, dr)
                    # print precision, relative_predictions, itr_change, \
                    #     current_itr, itr_calculator2.itrFromPrecisionPredictions(precision, relative_predictions)

                    indices = self.calculateNewIndices(itr_change, indices, lengths, step)
                    # indices = map(lambda (x, y): y+int(np.sign(x*step)*np.ceil(np.abs(x*step))), zip(itr_change, indices))
                    # no_difference = [j >= length or j < 0 for j, length in zip(indices, lengths)]
                    # if any(no_difference):
                    #     # print "Reached end of array! Cannot calculate derivative"
                    #     for j, no in enumerate(no_difference):
                    #         if no:
                    #             self.throwToMiddle(indices, lengths, j)

                    # max_change = np.argmax(abs(itr_change))
                    # if itr_change[max_change] > 0:
                    #     if indices[max_change] >= lengths[max_change]-1:
                    #         print "Reached start of an array! Cannot increase index"
                    #         self.throwToMiddle(indices, max_change, lengths[max_change])
                    #     else:
                    #         indices[max_change] += step
                    # elif itr_change[max_change] < 0:
                    #     if indices[max_change] <= 0:
                    #         print "Reached start of an array! Cannot decrease index"
                    #         self.throwToMiddle(indices, max_change, lengths[max_change])
                    #     else:
                    #         indices[max_change] -= step
                    # elif itr_change[max_change] == 0:
                    #     print "No change in ITR"
                    if indices in previous_points:
                        # print "Been here already"
                        # print indices, previous_points
                        break
                    # print indices
                print k, len(itrs), max(itrs)
                # raw_input()
                indices = previous_points[np.argmax(itrs)]
                step -= 4
        return []
