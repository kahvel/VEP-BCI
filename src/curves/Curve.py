import sklearn.metrics


class Curve(object):
    def __init__(self, x=None, y=None, thresholds=None, auc=None, predictions=None):
        self.x = x
        self.y = y
        self.thresholds = thresholds
        self.auc = auc
        self.predictions = predictions

    def calculate(self, binary_labels, predictions):
        raise NotImplementedError("calculate not implemented!")

    def calculateCurve(self, binary_labels, predictions):
        raise NotImplementedError("calculateCurve not implemented!")

    def calculateAuc(self, a, b, average="macro"):
        raise NotImplementedError("calculateAuc not implemented!")

    def getValues(self):
        return self.x, self.y, self.thresholds, self.auc

    def getPredictions(self):
        return self.predictions


class RocCurve(Curve):
    """
    x = False positive rate
    y = True positive rate
    """
    def calculateCurve(self, binary_labels, predictions):
        self.x, self.y, self.thresholds = sklearn.metrics.roc_curve(binary_labels, predictions)

    def calculateAuc(self, x, y, average="macro"):
        self.auc = sklearn.metrics.auc(x, y)

    def calculate(self, binary_labels, predictions):
        self.calculateCurve(binary_labels, predictions)
        self.calculateAuc(self.x, self.y)
        return self


class PrecisionRecallCurve(Curve):
    """
    x = Recall
    y = Precision
    """
    def calculateCurve(self, binary_labels, predictions):
        self.y, self.x, self.thresholds = sklearn.metrics.precision_recall_curve(binary_labels, predictions)

    def calculateAuc(self, binary_labels, predictions, average="macro"):
        self.auc = sklearn.metrics.average_precision_score(binary_labels, predictions, average=average)

    def calculate(self, binary_labels, predictions):
        self.calculateCurve(binary_labels, predictions)
        self.calculateAuc(binary_labels, predictions)
        return self
