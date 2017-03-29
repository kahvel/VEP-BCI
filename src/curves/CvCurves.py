import numpy as np
import matplotlib.pyplot as plt

from curves import AverageCurve


class CvCurve(object):
    def __init__(self, ordered_labels):
        self.ordered_labels = ordered_labels
        self.n_splits = None
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
        self.n_splits = len(predictions)
        curves = self.crossValidationCurves(predictions, split_labels)
        self.curves_by_class = self.groupCurvesByClass(curves)
        self.addMeanCurves(self.curves_by_class)
        return self

    def plot(self):
        plt.figure()
        n_subplots = np.ceil(self.n_splits**0.5)
        for i, (label, curve) in enumerate(self.curves_by_class.items()):
            plt.subplot(n_subplots, n_subplots, i+1)
            curve.makePlot()
            self.setPlotTitle(label)
        plt.show()

    def setPlotTitle(self, label):
        raise NotImplementedError("setPlotTitle not implemented!")

    def getAverageCurve(self, ordered_labels):
        raise NotImplementedError("getAverageCurve not implemented!")

    def getCurve(self, n_curves):
        raise NotImplementedError("getCurve not implemented!")

    def calculateThresholds(self):
        cut_off_threshold = []
        for key in self.ordered_labels:
            _, y, thresholds, _ = self.curves_by_class[key].curves["macro"].getValues()
            cut_off_threshold.append(thresholds[np.argmax(y[:-1])])
        return cut_off_threshold


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
