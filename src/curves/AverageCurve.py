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

    def getCurve(self):
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
            curve = self.getCurve()
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

    def calculateThresholds(self):
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

    def getCurve(self):
        return Curve.RocCurve()

    def setPlotLabels(self):
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC curve')

    # def calculateThresholds(self, fpr_threshold=0.05):
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

    def getCurve(self):
        return Curve.PrecisionRecallCurve()

    def setPlotLabels(self):
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-recall curve')

    def calculateThresholds(self):
        cut_off_threshold = []
        for key in self.ordered_labels:
            _, y, thresholds, _ = self.curves[key].getValues()
            cut_off_threshold.append(thresholds[np.argmax(y[:-1])])
        return cut_off_threshold