from parsers import FeaturesParser
from training import LdaModel, DataCollectors
import constants as c

import numpy as np
import sklearn.metrics
import scipy
from sklearn.cross_validation import cross_val_predict


class ModelTrainer(object):
    def __init__(self):
        self.recordings = []
        self.features_to_use = None
        self.extraction_method_names = None
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

    def setRecordings(self, recordings):
        self.recordings = recordings

    def setup(self, options):
        self.setFeatureAndExtractionNames(options[c.MODELS_PARSE_FEATURES_TO_USE])
        self.look_back_length = options[c.MODELS_PARSE_LOOK_BACK_LENGTH]
        self.cross_validation_folds = options[c.MODELS_PARSE_CV_FOLDS]
        self.training_recordings = [self.recordings[i] for i in options[c.MODELS_PARSE_RECORDING_FOR_TRAINING]]
        self.validation_recordings = [self.recordings[i] for i in options[c.MODELS_PARSE_RECORDING_FOR_VALIDATION]]

    def setFeatureAndExtractionNames(self, features_to_use):
        self.features_to_use = self.getFeaturesToUse(features_to_use)
        self.extraction_method_names = self.getExtractionMethodNames(self.features_to_use)
        print features_to_use, self.extraction_method_names
        self.printWarningIfBadFeatures(features_to_use)

    def getFeaturesToUse(self, features_to_use):
        if features_to_use is None:
            return self.getHeaderOfFirstRecording()
        else:
            return features_to_use

    def printWarningIfBadFeatures(self, features_to_use):
        if not self.checkFeatures(features_to_use):
            print "Recordings are missing features!"

    def getHeaderOfFirstRecording(self):
        return self.recordings[0].getDataFileHeader()

    def allFeaturesInRecordings(self, features_to_use):
        return all(feature in recording.getDataFileHeader() for feature in features_to_use for recording in self.recordings)

    def allRecordingsSameFeatures(self):
        return all(self.getHeaderOfFirstRecording() == recording.getDataFileHeader() for recording in self.recordings)

    def checkFeatures(self, features_to_use):
        if features_to_use is None:
            return self.allRecordingsSameFeatures()
        else:
            return self.allFeaturesInRecordings(features_to_use)

    def getAllLookBackRatioMatrices(self, recordings, model):
        all_matrices = []
        all_labels = []
        for recording in recordings:
            collector = DataCollectors.TrainingCollector(self.look_back_length)
            ratio_matrix = model.buildRatioMatrix(recording)
            look_back_ratio_matrix, labels = collector.combineSamples(ratio_matrix, recording.expected_targets)
            all_matrices.append(look_back_ratio_matrix)
            all_labels.append(labels)
        return all_matrices, all_labels

    def getConcatenatedMatrix(self, recordings, model):
        matrices, labels = self.getAllLookBackRatioMatrices(recordings, model)
        data_matrix = np.concatenate(matrices, axis=0)
        data_labels = np.concatenate(labels, axis=0)
        return data_matrix, data_labels

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

    def getDecisionFunctionValues(self, model, data, use_proba=False):  # TODO remove loop
        predictions = []
        for features in data:
            if not use_proba:
                predictions.append(model.decisionFunction([features])[0])
            else:
                predictions.append(model.predict_proba([features])[0])
        return predictions

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
        minimum = self.findMin(self.recordings)
        maximum = self.findMax(self.recordings)
        model = LdaModel.LdaModel()
        model.setupNoThreshold(minimum, maximum, self.extraction_method_names)
        training_data, training_labels = self.getConcatenatedMatrix(self.training_recordings, model)
        model.fit(training_data, training_labels)
        label_order = model.getOrderedLabels()
        # training_confusion_matrix = self.getConfusionMatrix(model, training_data, training_labels, label_order)
        # cross_validation_prediction = cross_val_predict(model, training_data, training_labels, cv=self.cross_validation_folds)
        # cross_validation_confusion_matrix = sklearn.metrics.confusion_matrix(training_labels, cross_validation_prediction, labels=label_order)
        validation_data, validation_labels = self.getConcatenatedMatrix(self.validation_recordings, model)
        # validation_confusion_matrix = self.getConfusionMatrix(model, validation_data, validation_labels, label_order)
        validation_roc = self.calculateRoc(model, validation_data, validation_labels, label_order)
        thresholds = self.calculateThresholds(validation_roc, label_order)
        training_roc = self.calculateRoc(model, training_data, training_labels, label_order)
        self.model = model
        self.training_data = training_data
        self.training_labels = training_labels
        self.validation_data = validation_data
        self.validation_labels = validation_labels
        self.thresholds = thresholds
        self.min_max = minimum, maximum
        self.training_roc = training_roc
        self.validation_roc = validation_roc

    def getExtractionMethodNames(self, features):
        return sorted(set(FeaturesParser.getMethodFromFeature(feature) for feature in features))

    def findExtremum(self, function, recordings):
        extrema = {method: [] for method in self.extraction_method_names}
        for recording in recordings:
            for method, column in recording.iterateColumns(self.extraction_method_names):
                extrema[method].append(function(column))
        return {method: function(extrema[method]) for method in self.extraction_method_names}

    def findMin(self, recordings):
        return self.findExtremum(min, recordings)

    def findMax(self, recordings):
        return self.findExtremum(max, recordings)

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
