import numpy as np
import sklearn.metrics
import scipy
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.cross_validation import cross_val_predict

import constants as c


class ModelTrainer(object):
    def __init__(self):
        self.recordings = []
        self.features_to_use = None
        self.look_back_length = None
        self.cross_validation_folds = None
        self.training_recordings = []
        self.validation_recordings = []
        self.model = None
        self.training_data = None
        self.training_labels = None
        self.validation_data = None
        self.validation_labels = None
        self.thresholds = None
        self.min_max = None
        self.validation_roc = None
        self.training_roc = None

    def setRecordings(self, recordings):
        self.recordings = recordings

    def setup(self, options):
        self.setFeaturesToUse(options[c.CLASSIFICATION_PARSE_FEATURES_TO_USE])
        self.look_back_length = options[c.CLASSIFICATION_PARSE_LOOK_BACK_LENGTH]
        self.cross_validation_folds = options[c.CLASSIFICATION_PARSE_CV_FOLDS]
        self.training_recordings = [self.recordings[i] for i in options[c.CLASSIFICATION_PARSE_RECORDING_FOR_TRAINING]]
        self.validation_recordings = [self.recordings[i] for i in options[c.CLASSIFICATION_PARSE_RECORDING_FOR_VALIDATION]]

    def setFeaturesToUse(self, features_to_use):
        self.features_to_use = self.getFeaturesToUse(features_to_use)
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

    def buildDataMatrix(self, recording):
        return [column for method, column in self.iterateColumns(recording)]

    def buildScaledDataMatrix(self, recording, scaling_functions):
        return [scaling_functions[method](column) for method, column in self.iterateColumns(recording)]

    def getScaledColumnsGroupedByMethod(self, recording, scaling_functions):
        grouped_columns = {method: [] for method in self.getExtractionMethodNames()}
        for method, column in self.iterateColumns(recording):
            grouped_columns[method].append(map(scaling_functions[method], column))
        return grouped_columns

    def getGroupRatioRows(self, group):
        rows = []
        for grouped_features in zip(*group):
            rows.append([grouped_features[j]/sum(grouped_features) for j in range(len(grouped_features))])
        return rows

    def getRatioRowsGroupedByMethod(self, grouped_columns):
        return {method: self.getGroupRatioRows(grouped_columns[method]) for method in self.getExtractionMethodNames()}

    def concatenateMatricesOfRows(self, grouped_rows):
        extraction_method_names = self.getExtractionMethodNames()
        result = grouped_rows[extraction_method_names[0]]
        for method in extraction_method_names[1:]:
            result = np.concatenate((result, grouped_rows[method]), axis=1)
        return result

    def buildRatioMatrix(self, recording, scaling_functions):
        grouped_columns = self.getScaledColumnsGroupedByMethod(recording, scaling_functions)
        grouped_rows = self.getRatioRowsGroupedByMethod(grouped_columns)
        return self.concatenateMatricesOfRows(grouped_rows)

    def extendNewSample(self, previous_labels, sample_count, new_data, new_sample, sample, label, new_labels):
        if len(previous_labels) == sample_count:
            if all(map(lambda x: x == previous_labels[0], previous_labels)):
                new_data.append(np.concatenate(new_sample))
                new_labels.append(previous_labels[0])
            del previous_labels[0]
            del new_sample[0]
            previous_labels.append(label)
            new_sample.append(sample)
        else:
            previous_labels.append(label)
            new_sample.append(sample)

    def groupWithPreviousSamples(self, matrix, labels, sample_count):
        new_data = []
        new_labels = []
        previous_labels = []
        new_sample = []
        for sample, label in zip(matrix, labels):
            self.extendNewSample(previous_labels, sample_count, new_data, new_sample, sample, label, new_labels)
        self.extendNewSample(previous_labels, sample_count, new_data, new_sample, sample, label, new_labels)
        return np.array(new_data), new_labels

    def getAllLookBackRatioMatrices(self, scaling_functions, recordings):
        all_matrices = []
        all_labels = []
        for recording in recordings:
            ratio_matrix = self.buildRatioMatrix(recording, scaling_functions)
            look_back_ratio_matrix, labels = self.groupWithPreviousSamples(ratio_matrix, recording.expected_targets, self.look_back_length)
            all_matrices.append(look_back_ratio_matrix)
            all_labels.append(labels)
        return all_matrices, all_labels

    def getConcatenatedMatrix(self, recordings, scaling_functions):
        matrices, labels = self.getAllLookBackRatioMatrices(scaling_functions, recordings)
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

    def getDecisionFunctionValues(self, model, data, use_prediction=False):  # TODO remove loop
        predictions = []
        for features in data:
            if not use_prediction:
                predictions.append(model.decision_function([features])[0])
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
        scaling_functions = self.getScalingFunctions(minimum, maximum)
        training_data, training_labels = self.getConcatenatedMatrix(self.training_recordings, scaling_functions)
        model = LinearDiscriminantAnalysis()
        model.fit(training_data, training_labels)
        label_order = model.classes_
        # training_confusion_matrix = self.getConfusionMatrix(model, training_data, training_labels, label_order)
        # cross_validation_prediction = cross_val_predict(model, training_data, training_labels, cv=self.cross_validation_folds)
        # cross_validation_confusion_matrix = sklearn.metrics.confusion_matrix(training_labels, cross_validation_prediction, labels=label_order)
        validation_data, validation_labels = self.getConcatenatedMatrix(self.validation_recordings, scaling_functions)
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

    def getMethodFromFeature(self, feature):
        return "_".join(feature.split("_")[:-1])

    def getExtractionMethodNames(self):
        return sorted(set(self.getMethodFromFeature(feature) for feature in self.features_to_use))

    def iterateColumns(self, recording):
        extraction_method_names = self.getExtractionMethodNames()
        columns = recording.getColumnsAsFloats(recording.data)
        for key in sorted(columns):
            method = self.getMethodFromFeature(key)
            if method in extraction_method_names:
                yield method, columns[key]

    def findExtremum(self, function, recordings):
        extraction_method_names = self.getExtractionMethodNames()
        extrema = {method: [] for method in extraction_method_names}
        for recording in recordings:
            for method, column in self.iterateColumns(recording):
                extrema[method].append(function(column))
        return {method: function(extrema[method]) for method in extraction_method_names}

    def findMin(self, recordings):
        return self.findExtremum(min, recordings)

    def findMax(self, recordings):
        return self.findExtremum(max, recordings)

    def getScalingFunction(self, minimum, maximum):
        return lambda x: (x-minimum)/(maximum-minimum)+1

    def getScalingFunctions(self, minimums, maximums):
        return {method: self.getScalingFunction(minimums[method], maximums[method]) for method in self.getExtractionMethodNames()}

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
