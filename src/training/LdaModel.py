from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import numpy as np


class LdaModel(object):
    def __init__(self):
        self.model = None
        self.thresholds = None
        self.minimum = None
        self.maximum = None
        self.extraction_method_names = None
        self.scaling_functions = None
        self.matrix_builder = None

    def setupNoThreshold(self, minimum, maximum, extraction_method_names):
        self.minimum = minimum
        self.maximum = maximum
        self.extraction_method_names = extraction_method_names
        self.scaling_functions = ScalingFunctions(minimum, maximum, extraction_method_names)
        self.model = LinearDiscriminantAnalysis()
        self.matrix_builder = MatrixBuilder(self.scaling_functions, self.extraction_method_names)

    def buildRatioMatrix(self, data):
        return self.matrix_builder.buildRatioMatrix(data)

    def getOrderedLabels(self):
        return self.model.classes_

    def fit(self, data, labels):
        self.model.fit(data, labels)

    def decisionFunction(self, data):
        return self.model.decision_function(data)  # value depends on the number of classes!


class ScalingFunctions(object):
    def __init__(self, minima, maxima, extraction_method_names):
        self.scaling_functions = self.getScalingFunctions(minima, maxima, extraction_method_names)

    def __getitem__(self, item):
        return self.scaling_functions[item]

    def getScalingFunction(self, minimum, maximum):
        return lambda x: (x-minimum)/(maximum-minimum)+1

    def getScalingFunctions(self, minima, maxima, extraction_method_names):
        return {method: self.getScalingFunction(minima[method], maxima[method]) for method in extraction_method_names}


class MatrixBuilder(object):
    def __init__(self, scaling_functions, extraction_method_names):
        self.scaling_functions = scaling_functions
        self.extraction_method_names = extraction_method_names

    def buildRatioMatrix(self, recording):
        grouped_columns = self.getScaledColumnsGroupedByMethod(recording)
        grouped_rows = self.getRatioRowsGroupedByMethod(grouped_columns)
        return self.concatenateMatricesOfRows(grouped_rows)

    def getScaledColumnsGroupedByMethod(self, recording):
        grouped_columns = {method: [] for method in self.extraction_method_names}
        for method, column in recording.iterateColumns(self.extraction_method_names):
            grouped_columns[method].append(map(self.scaling_functions[method], column))
        return grouped_columns

    def getRatioRowsGroupedByMethod(self, grouped_columns):
        return {method: self.getGroupRatioRows(grouped_columns[method]) for method in self.extraction_method_names}

    def concatenateMatricesOfRows(self, grouped_rows):
        result = grouped_rows[self.extraction_method_names[0]]
        for method in self.extraction_method_names[1:]:
            result = np.concatenate((result, grouped_rows[method]), axis=1)
        return result

    def getGroupRatioRows(self, group):
        rows = []
        for grouped_features in zip(*group):
            rows.append([grouped_features[j]/sum(grouped_features) for j in range(len(grouped_features))])
        return rows