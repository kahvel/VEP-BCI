import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt

from curves import AverageCurve


class CvCurve(object):
    def __init__(self, ordered_labels):
        self.ordered_labels = ordered_labels
        self.curves_by_class = None

    def crossValidationCurves(self, predictions, split_labels):
        folds = len(predictions)
        curves = []
        for i in range(folds):
            curve = self.getAverageCurve(self.ordered_labels)
            curve.calculate(np.transpose(predictions[i]), split_labels[i])
            curves.append(curve)
        return curves

    def groupCurvesByClass(self, curves):
        curves_by_class = dict()
        for i, curve in enumerate(curves):
            for label in curve.getClasses():
                if label not in curves_by_class:
                    curves_by_class[label] = self.getCurve(len(curves))
                curves_by_class[label].addCurve(curve.curves[label], i+1)
        return curves_by_class

    def addMeanCurves(self, curves_by_class):
        for label in curves_by_class:
            curves_by_class[label].addMacro()

    def calculate(self, predictions, split_labels):
        curves = self.crossValidationCurves(predictions, split_labels)
        return self.calculateFromCurves(curves)

    def calculateFromCurves(self, curves):
        self.curves_by_class = self.groupCurvesByClass(curves)
        self.addMeanCurves(self.curves_by_class)
        return self

    def plot(self, num=1):
        plt.figure(num)
        n_subplots = np.ceil(len(self.ordered_labels)**0.5)
        for i, (label, curve) in enumerate(self.curves_by_class.items()):
            plt.subplot(n_subplots, n_subplots, i+1)
            curve.makePlot()
            self.setPlotTitle(label)
        plt.draw()

    def setPlotTitle(self, label):
        raise NotImplementedError("setPlotTitle not implemented!")

    def getAverageCurve(self, ordered_labels):
        raise NotImplementedError("getAverageCurve not implemented!")

    def getCurve(self, n_curves):
        raise NotImplementedError("getCurve not implemented!")

    def getAllMacroAverageThresholds(self):
        all_thresholds = []
        for key in self.ordered_labels:
            _, _, thresholds, _ = self.curves_by_class[key].curves["macro"].getValues()
            all_thresholds.append(thresholds)
        return all_thresholds

    def calculateThresholds(self, optimisation_function):
        # cut_off_threshold1 = []  # Threshold from macro-average curve
        # for key in self.ordered_labels:
        #     _, y, thresholds, _ = self.curves_by_class[key].curves["macro"].getValues()
        #     cut_off_threshold1.append(thresholds[np.argmax(y[:-1])])
        # return cut_off_threshold1
        cut_off_threshold = []  # Threshold as mean over individual thresholds
        for key in self.ordered_labels:
            thresholds = self.curves_by_class[key].calculateThresholds(optimisation_function)
            cut_off_threshold.append(np.mean(thresholds))
        return cut_off_threshold
        # return (np.array(cut_off_threshold1) + np.array(cut_off_threshold))/2.0
        # macro_averages = self.getAllMacroAverageThresholds()  # Brute force (takes way too long...)
        # ranges = list((0, length, 1) for length in map(len, macro_averages))
        # print ranges
        # scipy.optimize.brute(optimisation_function, ranges, args=(macro_averages,))


class RocCvCurve(CvCurve):
    def setPlotTitle(self, label):
        plt.title('ROC curve of class ' + str(label))

    def getCurve(self, n_curves):
        return RocCurve(list(range(1, n_curves+1)))

    def getAverageCurve(self, ordered_labels):
        return AverageCurve.AverageRocCurve(ordered_labels)


class PrecisionRecallCvCurve(CvCurve):
    def setPlotTitle(self, label):
        plt.title('Precision-recall curve of class ' + str(label))

    def getCurve(self, n_curves):
        return PrecisionRecallCurve(list(range(1, n_curves+1)))

    def getAverageCurve(self, ordered_labels):
        return AverageCurve.AveragePrecisionRecallCurve(ordered_labels)


class RocCurve(AverageCurve.AverageRocCurve):
    def getCurveLegendLabel(self, key):
        if isinstance(key, int):
            return 'Split {0}'.format(key)
        elif key in ["micro", "macro"]:
            return key + '-average'

    def addCurve(self, curve, split):
        self.curves[split] = curve


class PrecisionRecallCurve(AverageCurve.AveragePrecisionRecallCurve):
    def getCurveLegendLabel(self, key):
        if isinstance(key, int):
            return 'Split {0}'.format(key)
        elif key in ["micro", "macro"]:
            return key + '-average'

    def addCurve(self, curve, split):
        self.curves[split] = curve

    def getThresholds(self):
        all_thresholds = []
        for key in self.ordered_labels:
            _, _, thresholds, _ = self.curves[key].getValues()
            all_thresholds.append(thresholds)
        return all_thresholds

    def getMeanThreshold(self):
        return np.mean(self.getThresholds(), axis=0)

    def calculateThresholds(self, optimisation_function):
        cut_off_threshold = []  # Threshold with max ITR
        for key in self.ordered_labels:
            x, y, thresholds, _ = self.curves[key].getValues()
            itrs = map(lambda (r, p): optimisation_function(p, r), zip(x, y))
            cut_off_threshold.append(thresholds[np.argmax(itrs[:-1])])
        return cut_off_threshold

