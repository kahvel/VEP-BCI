import numpy as np
import sklearn.metrics
import scipy

from target_identification import LdaModel
import constants as c


class ModelTrainer(object):
    def __init__(self):
        self.recordings = []
        self.look_back_length = None
        self.cross_validation_folds = None
        self.training_recordings = []
        self.validation_recordings = []
        self.training_data = None
        self.training_labels = None
        self.validation_data = None
        self.validation_labels = None
        self.validation_roc = None
        self.training_roc = None
        self.model = None
        self.thresholds = None
        self.min_max = None

    def setRecordings(self, recordings):
        self.recordings = recordings

    def setup(self, options):
        features_to_use = options[c.MODELS_PARSE_FEATURES_TO_USE]
        self.look_back_length = options[c.MODELS_PARSE_LOOK_BACK_LENGTH]
        self.cross_validation_folds = options[c.MODELS_PARSE_CV_FOLDS]
        self.training_recordings = [self.recordings[i] for i in options[c.MODELS_PARSE_RECORDING_FOR_TRAINING]]
        self.validation_recordings = [self.recordings[i] for i in options[c.MODELS_PARSE_RECORDING_FOR_VALIDATION]]
        self.model = LdaModel.TrainingLdaModel()
        self.model.setup(features_to_use, self.look_back_length, self.recordings)

    def getConfusionMatrix(self, model, data, labels, label_order):
        prediction = model.predict(data)
        return sklearn.metrics.confusion_matrix(labels, prediction, labels=label_order)

    def calculateBinaryRoc(self, predictions, binary_labels, labels_order):
        predictions = np.transpose(predictions)
        fpr = dict()
        tpr = dict()
        thresholds = dict()
        roc_auc = dict()
        for i in range(len(labels_order)):
            fpr[i], tpr[i], thresholds[i] = sklearn.metrics.roc_curve(binary_labels[i], predictions[i])
            roc_auc[i] = sklearn.metrics.auc(fpr[i], tpr[i])
        return fpr, tpr, thresholds, roc_auc

    def addMicroRoc(self, roc, predictions, binary_labels):
        predictions = np.array(predictions)
        fpr, tpr, _, roc_auc = roc
        fpr["micro"], tpr["micro"], _ = sklearn.metrics.roc_curve(np.array(binary_labels).ravel(), predictions.ravel())
        roc_auc["micro"] = sklearn.metrics.auc(fpr["micro"], tpr["micro"])

    def addMacroRoc(self, roc, labels_order):
        fpr, tpr, _, roc_auc = roc
        all_fpr = np.unique(np.concatenate([fpr[i] for i in range(len(labels_order))]))
        mean_tpr = np.zeros_like(all_fpr)
        for i in range(len(labels_order)):
            mean_tpr += scipy.interp(all_fpr, fpr[i], tpr[i])
        mean_tpr /= len(labels_order)
        fpr["macro"] = all_fpr
        tpr["macro"] = mean_tpr
        roc_auc["macro"] = sklearn.metrics.auc(fpr["macro"], tpr["macro"])

    def calculateThresholds(self, roc, labels_order, fpr_threshold=0.05):
        fpr, tpr, thresholds, _ = roc
        cut_off_threshold = []
        for i in range(len(labels_order)):
            for false_positive_rate, true_positive_rate, threshold in zip(fpr[i], tpr[i], thresholds[i]):
                if false_positive_rate > fpr_threshold:
                    cut_off_threshold.append(threshold)
                    break
            else:
                print "Warning: no cutoff obtained!"
        return cut_off_threshold

    def getDecisionFunctionValues(self, model, data, use_proba=False):
        """
        If use_proba=False then the function does not work with less than 3 classes.
        :param model:
        :param data:
        :param use_proba:
        :return:
        """
        if use_proba:
            return model.decisionFunction(data)
        else:
            return model.predictProba(data)

    def getBinaryLabels(self, labels, label_order):
        binary_labels = []
        for label in label_order:
            binary_labels.append(list(map(lambda x: x == label, labels)))
        return binary_labels

    def calculateMulticlassRoc(self, decision_function_values, binary_labels, label_order):
        roc = self.calculateBinaryRoc(decision_function_values, binary_labels, label_order)
        self.addMicroRoc(roc, decision_function_values, binary_labels)
        self.addMacroRoc(roc, binary_labels)
        return roc

    def calculateRoc(self, model, data, labels, label_order):
        binary_labels = self.getBinaryLabels(labels, label_order)
        decision_function_values = self.getDecisionFunctionValues(model, data)
        return self.calculateMulticlassRoc(decision_function_values, binary_labels, label_order)

    def start(self):
        training_data, training_labels = self.model.getConcatenatedMatrix(self.training_recordings)
        self.model.fit(training_data, training_labels)
        label_order = self.model.getOrderedLabels()
        # training_confusion_matrix = self.getConfusionMatrix(model, training_data, training_labels, label_order)
        # cross_validation_prediction = cross_val_predict(model, training_data, training_labels, cv=self.cross_validation_folds)
        # cross_validation_confusion_matrix = sklearn.metrics.confusion_matrix(training_labels, cross_validation_prediction, labels=label_order)
        validation_data, validation_labels = self.model.getConcatenatedMatrix(self.validation_recordings)
        # validation_confusion_matrix = self.getConfusionMatrix(model, validation_data, validation_labels, label_order)
        validation_roc = self.calculateRoc(self.model, validation_data, validation_labels, label_order)
        thresholds = self.calculateThresholds(validation_roc, label_order)
        training_roc = self.calculateRoc(self.model, training_data, training_labels, label_order)
        self.training_data = training_data
        self.training_labels = training_labels
        self.validation_data = validation_data
        self.validation_labels = validation_labels
        self.thresholds = thresholds
        self.min_max = self.model.getMinMax()
        self.model = self.model.model
        self.training_roc = training_roc
        self.validation_roc = validation_roc

    def getModel(self):
        return self.model

    def getTrainingData(self):
        return self.training_data

    def getTrainingLabels(self):
        return self.training_labels

    def getValidationData(self):
        return self.validation_data

    def getValidationLabels(self):
        return self.validation_labels

    def getThresholds(self):
        return self.thresholds

    def getMinMax(self):
        return self.min_max

    def getTrainingRoc(self):
        return self.training_roc

    def getValidationRoc(self):
        return self.validation_roc
