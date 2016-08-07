import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import confusion_matrix
from sklearn.cross_validation import cross_val_predict


class ModelTrainer(object):
    def __init__(self):
        self.target_count = None
        self.recordings = []
        self.features_to_use = None
        self.look_back_length = None
        self.cross_validation_folds = 5

    def setup(self):
        self.target_count = 3
        self.recordings = []

    def buildDataMatrix(self, recording):
        return [column for method, column in self.iterateColumns(recording)]

    def buildScaledDataMatrix(self, recording, scaling_functions):
        return [scaling_functions[method](column) for method, column in self.iterateColumns(recording)]

    def getScaledColumnsGroupedByMethod(self, recording, scaling_functions):
        grouped_columns = {method: [] for method in self.getExtractionMethodNames()}
        for method, column in self.iterateColumns(recording):
            grouped_columns[method].append(scaling_functions[method](column))
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

    def getAllLookBackRatioMatrices(self, scaling_functions):
        all_matrices = []
        all_labels = []
        for recording in self.recordings:
            ratio_matrix = self.buildRatioMatrix(recording, scaling_functions)
            look_back_ratio_matrix, labels = self.groupWithPreviousSamples(ratio_matrix, recording.expected_targets)
            all_matrices.append(look_back_ratio_matrix)
            all_labels.append(labels)
        return all_matrices, all_labels

    def start(self):
        minimum = self.getMin()
        maximum = self.getMax()
        scaling_functions = self.getScalingFunctions(minimum, maximum)
        matrices, labels = self.getAllLookBackRatioMatrices(scaling_functions)
        data_matrix = np.concatenate(matrices, axis=0)
        data_labels = np.concatenate(labels, axis=0)
        model = LinearDiscriminantAnalysis()
        model.fit(data_matrix, data_labels)
        prediction = model.predict(data_matrix)
        training_confusion_matrix = confusion_matrix(data_labels, prediction)
        cross_validation_prediction = cross_val_predict(model, data_matrix, data_labels, cv=self.cross_validation_folds)
        cross_validation_confusion_matrix = confusion_matrix(data_labels, cross_validation_prediction)

    def setFeaturesToUse(self, features_to_use):
        if features_to_use is None:
            self.features_to_use = None
        else:
            self.features_to_use = sorted(features_to_use)

    def getMethodFromFeature(self, feature):
        return "_".join(feature.split("_")[:-1])

    def getExtractionMethodNames(self):
        return sorted(set(self.getMethodFromFeature(feature) for feature in self.features_to_use))

    def allFeaturesInRecordings(self):
        return all(feature in recording.getDataFileHeader() for feature in self.features_to_use for recording in self.recordings)

    def allRecordingsSameFeatures(self):
        return all(self.recordings[0].getDataFileHeader() == recording.getDataFileHeader() for recording in self.recordings)

    def checkFeatures(self):
        if self.features_to_use is None:
            return self.allRecordingsSameFeatures()
        else:
            return self.allFeaturesInRecordings()

    def iterateColumns(self, recording):
        extraction_method_names = self.getExtractionMethodNames()
        columns = recording.getColumns()
        for key in sorted(columns):
            method = self.getMethodFromFeature(key)
            if method in extraction_method_names:
                yield method, columns[key]

    def getExtremum(self, function):
        extraction_method_names = self.getExtractionMethodNames()
        extrema = {method: [] for method in extraction_method_names}
        for recording in self.recordings:
            for method, column in self.iterateColumns(recording):
                extrema[method].append(function(column))
        return {method: min(extrema[method]) for method in extraction_method_names}

    def getMin(self):
        return self.getExtremum(min)

    def getMax(self):
        return self.getExtremum(max)

    def getScalingFunctions(self, minimums, maximums):
        return {method: lambda x: (x-minimums[method])/(maximums[method]-minimums[method]) for method in self.getExtractionMethodNames()}
