from training import DataCollectors, MatrixBuilder

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis


class LdaModel(object):
    def __init__(self):
        self.model = None
        self.thresholds = None
        self.minimum = None
        self.maximum = None
        self.extraction_method_names = None
        self.scaling_functions = None
        self.collector = None
        self.matrix_builder = None

    def setupNoThreshold(self, minimum, maximum, extraction_method_names):
        self.minimum = minimum
        self.maximum = maximum
        self.extraction_method_names = extraction_method_names
        self.scaling_functions = ScalingFunctions(minimum, maximum, extraction_method_names)
        self.model = LinearDiscriminantAnalysis()
        self.matrix_builder.setup(self.scaling_functions, self.extraction_method_names)

    def buildRatioMatrix(self, data):
        return self.matrix_builder.buildRatioMatrix(data)

    def collectSamples(self, *args):
        raise NotImplementedError("collectSamples not implemented!")

    def getOrderedLabels(self):
        return self.model.classes_

    def fit(self, data, labels):
        self.model.fit(data, labels)

    def decisionFunction(self, data):
        return self.model.decision_function(data)  # value depends on the number of classes!


class ScalingFunctions(object):
    def __init__(self, minima, maxima, extraction_method_names):
        self.minima = minima
        self.maxima = maxima
        self.scaling_functions = self.getScalingFunctions(minima, maxima, extraction_method_names)

    def __getitem__(self, item):
        return self.scaling_functions[item]

    def getScalingFunction(self, minimum, maximum):
        return lambda x: (x-minimum)/(maximum-minimum)+1

    def getScalingFunctions(self, minima, maxima, extraction_method_names):
        return {method: self.getScalingFunction(minima[method], maxima[method]) for method in extraction_method_names}


class TrainingLdaModel(LdaModel):
    def __init__(self, sample_count):
        LdaModel.__init__(self)
        self.collector = DataCollectors.TrainingCollector(sample_count)
        self.matrix_builder = MatrixBuilder.TrainingMatrixBuilder()

    def collectSamples(self, features, labels):
        return self.collector.combineSamples(features, labels)


class OnlineLdaModel(LdaModel):
    def __init__(self, sample_count):
        LdaModel.__init__(self)
        self.collector = DataCollectors.OnlineCollector(sample_count)
        self.matrix_builder = MatrixBuilder.OnlineMatrixBuilder()

    def collectSamples(self, features):
        return self.collector.handleSample(features)
