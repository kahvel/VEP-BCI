import numpy as np
import sklearn.metrics
import scipy


class Curve(object):
    def __init__(self):
        self.x = dict()
        self.y = dict()
        self.thresholds = dict()
        self.auc = dict()

    def calculateBinary(self, predictions, binary_labels, labels_order):
        for i in range(len(labels_order)):
            self.x[i], self.y[i], self.thresholds[i] = self.calculateCurve(binary_labels[i], predictions[i])
            self.auc[i] = self.calculateAuc(binary_labels[i], predictions[i], self.x[i], self.y[i])
        return self.x, self.y, self.thresholds, self.auc

    def calculateCurve(self, binary_labels, predictions):
        raise NotImplementedError("calculateCurve not implemented!")

    def calculateAuc(self, binary_labels, predictions, x, y, average="macro"):
        raise NotImplementedError("calculateAuc not implemented!")

    def addMicro(self, predictions, binary_labels):
        self.x["micro"], self.y["micro"], _ = self.calculateCurve(np.array(binary_labels).ravel(), predictions.ravel())
        self.auc["micro"] = self.calculateAuc(np.array(binary_labels), predictions, self.x["micro"], self.y["micro"], average="micro")

    def addMacro(self, labels_order):
        raise NotImplementedError("addMacro not implemented!")

    def getBinaryLabels(self, labels, label_order):
        binary_labels = []
        for label in label_order:
            binary_labels.append(list(map(lambda x: x == label, labels)))
        return binary_labels

    def calculateMulticlass(self, decision_function_values, binary_labels, label_order):
        self.calculateBinary(decision_function_values, binary_labels, label_order)
        self.addMicro(decision_function_values, binary_labels)
        self.addMacro(label_order)
        return self.x, self.y, self.thresholds, self.auc

    def calculate(self, decision_function_values, labels, label_order):
        binary_labels = self.getBinaryLabels(labels, label_order)
        return self.calculateMulticlass(decision_function_values, binary_labels, label_order)


class RocCurve(Curve):
    """
    x = False positive rate
    y = True positive rate
    """
    def calculateCurve(self, binary_labels, predictions):
        return sklearn.metrics.roc_curve(binary_labels, predictions)

    def calculateAuc(self, binary_labels, predictions, x, y, average="macro"):
        return sklearn.metrics.auc(x, y)

    def addMacro(self, labels_order):
        all_fpr = np.unique(np.concatenate([self.x[i] for i in range(len(labels_order))]))
        mean_tpr = np.zeros_like(all_fpr)
        for i in range(len(labels_order)):
            mean_tpr += scipy.interp(all_fpr, self.x[i], self.y[i])
        mean_tpr /= len(labels_order)
        self.x["macro"] = all_fpr
        self.y["macro"] = mean_tpr
        self.auc["macro"] = sklearn.metrics.auc(self.x["macro"], self.y["macro"])


class PrecisionRecallCurve(Curve):
    """
    x = Recall
    y = Precision
    """
    def calculateCurve(self, binary_labels, predictions):
        precision, recall, thresholds = sklearn.metrics.precision_recall_curve(binary_labels, predictions)
        return recall, precision, thresholds

    def calculateAuc(self, binary_labels, predictions, x, y, average="macro"):
        return sklearn.metrics.average_precision_score(binary_labels, predictions, average=average)

    def addMacro(self, labels_order):
        pass


