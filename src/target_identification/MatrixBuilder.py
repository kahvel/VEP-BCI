import numpy as np


class MatrixBuilder(object):
    def __init__(self):
        self.scaling_functions = None
        self.extraction_method_names = None
        self.calculate_ratios = None

    def setup(self, scaling_functions, extraction_method_names, calculate_ratios):
        self.scaling_functions = scaling_functions
        self.extraction_method_names = extraction_method_names
        self.calculate_ratios = calculate_ratios

    def buildRatioMatrix(self, columns):
        grouped_columns = self.getScaledColumnsGroupedByMethod(columns)
        grouped_rows = self.getRatioRowsGroupedByMethod(grouped_columns)
        return self.concatenateMatricesOfRows(grouped_rows)

    def scaleColumn(self, method, column):
        raise NotImplementedError("scaleColumn not implemented!")

    def getScaledColumnsGroupedByMethod(self, columns):
        grouped_columns = {method: [] for method in self.extraction_method_names}
        for method, column in columns:
            grouped_columns[method].append(self.scaleColumn(method, column))
            # print method
            # print "Features", column
            # print "Scaled  ", self.scaleColumn(method, column)
            # print self.scaling_functions.minima[method], self.scaling_functions.maxima[method]
        return grouped_columns

    def getRatioRowsGroupedByMethod(self, grouped_columns):
        return {method: self.getGroupRatioRows(grouped_columns[method]) for method in self.extraction_method_names}

    def concatenateMatricesOfRows(self, grouped_rows):
        result = grouped_rows[self.extraction_method_names[0]]
        for method in self.extraction_method_names[1:]:
            result = np.concatenate((result, grouped_rows[method]), axis=1)
        return result

    def iterateGroupedColumns(self, group):
        raise NotImplementedError("iterateGroupedColumns not implemented!")

    def getGroupRatioRows(self, group):
        rows = []
        for grouped_features in self.iterateGroupedColumns(group):
            rows.append([self.calculateRatios(grouped_features, j) for j in range(len(grouped_features))])
            # print grouped_features
            # print [grouped_features[j]/sum(grouped_features) for j in range(len(grouped_features))]
        return rows

    def calculateRatios(self, grouped_features, j):
        if self.calculate_ratios:
            return grouped_features[j]/sum(grouped_features)
        else:
            return grouped_features[j]


class TrainingMatrixBuilder(MatrixBuilder):
    def __init__(self):
        MatrixBuilder.__init__(self)

    def scaleColumn(self, method, column):
        return map(self.scaling_functions[method], column)

    def iterateGroupedColumns(self, group):
        return zip(*group)


class OnlineMatrixBuilder(MatrixBuilder):
    def __init__(self):
        MatrixBuilder.__init__(self)

    def scaleColumn(self, method, column):
        # print self.scaling_functions.minima[method], self.scaling_functions.maxima[method]
        return self.scaling_functions[method](column)

    def iterateGroupedColumns(self, group):
        return group,
