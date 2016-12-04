from target_identification import DataCollectors, MatrixBuilder, ScalingFunction, ColumnsIterator, FeaturesHandler

import numpy as np


class Model(ColumnsIterator.ColumnsIterator):
    def __init__(self):
        ColumnsIterator.ColumnsIterator.__init__(self)
        self.model = None
        self.thresholds = None
        self.extraction_method_names = None
        self.scaling_functions = None
        self.collector = None
        self.matrix_builder = None
        self.features_handler = None

    def setup(self, *args):
        raise NotImplementedError("setup not implemented!")

    def setupScalingFunctions(self, *args):
        raise NotImplementedError("setupScalingFunctions not implemented!")

    def setupFeaturesHandler(self, *args):
        raise NotImplementedError("setupFeaturesHandler not implemented!")

    def setupCollectorAndBuilder(self, sample_count, scaling_functions, extraction_method_names):
        raise NotImplementedError("setupCollectorAndBuilder not implemented!")

    def buildRatioMatrix(self, data):
        return self.matrix_builder.buildRatioMatrix(self.iterateColumns(data, self.extraction_method_names))

    def collectSamples(self, *args):
        raise NotImplementedError("collectSamples not implemented!")

    def getOrderedLabels(self):
        return self.model.classes_

    def fit(self, data, labels):
        self.model.fit(data, labels)

    def decisionFunction(self, data):
        raise NotImplementedError("decisionFunction not implemented")

    def predictProba(self, data):
        return self.model.predict_proba(data)

    def getMinMax(self):
        return self.scaling_functions.minima, self.scaling_functions.maxima

    def predict(self, data):
        return self.model.predict(data)


class TrainingModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.features_to_use = None

    def getModel(self):
        raise NotImplementedError("getModel not implemented!")

    def setup(self, features_to_use, sample_count, recordings):
        self.extraction_method_names = self.setupFeaturesHandler(features_to_use, recordings)
        self.setupScalingFunctions(self.extraction_method_names, recordings)
        self.model = self.getModel()
        self.setupCollectorAndBuilder(sample_count, self.scaling_functions, self.extraction_method_names)

    def setupScalingFunctions(self, extraction_method_names, recordings):
        self.scaling_functions = ScalingFunction.TrainingScalingFunctions()
        self.scaling_functions.setup(extraction_method_names, recordings)

    def setupCollectorAndBuilder(self, sample_count, scaling_functions, extraction_method_names):
        self.collector = DataCollectors.TrainingCollector(sample_count)
        self.matrix_builder = MatrixBuilder.TrainingMatrixBuilder()
        self.matrix_builder.setup(scaling_functions, extraction_method_names)

    def setupFeaturesHandler(self, features_to_use, recordings):
        self.features_handler = FeaturesHandler.TrainingFeaturesHandler(recordings)
        self.features_handler.setup(features_to_use)
        self.features_to_use = self.features_handler.getUsedFeatures()
        return self.features_handler.getExtractionMethodNames()

    def collectSamples(self, features, labels):
        return self.collector.combineSamples(features, labels)

    def getAllLookBackRatioMatrices(self, recordings):
        self.collector.reset()
        all_matrices = []
        all_labels = []
        for recording in recordings:
            ratio_matrix = self.buildRatioMatrix(recording.getColumnsAsFloats(recording.data))
            look_back_ratio_matrix, labels = self.collectSamples(ratio_matrix, recording.expected_targets)
            all_matrices.append(look_back_ratio_matrix)
            all_labels.append(labels)
        return all_matrices, all_labels

    def getConcatenatedMatrix(self, recordings):
        matrices, labels = self.getAllLookBackRatioMatrices(recordings)
        data_matrix = np.concatenate(matrices, axis=0)
        data_labels = np.concatenate(labels, axis=0)
        return data_matrix, data_labels

    def getUsedFeatures(self):
        return self.features_to_use


class OnlineModel(Model):
    def __init__(self):
        Model.__init__(self)

    def setup(self, minimum, maximum, features_to_use, sample_count, model):
        self.extraction_method_names = self.setupFeaturesHandler(features_to_use)
        self.setupScalingFunctions(minimum, maximum, self.extraction_method_names)
        self.model = model
        self.setupCollectorAndBuilder(sample_count, self.scaling_functions, self.extraction_method_names)

    def setupScalingFunctions(self, minimum, maximum, extraction_method_names):
        self.scaling_functions = ScalingFunction.OnlineScalingFunctions()
        self.scaling_functions.setup(minimum, maximum, extraction_method_names)

    def setupCollectorAndBuilder(self, sample_count, scaling_functions, extraction_method_names):
        self.collector = DataCollectors.OnlineCollector(sample_count)
        self.matrix_builder = MatrixBuilder.OnlineMatrixBuilder()
        self.matrix_builder.setup(scaling_functions, extraction_method_names)

    def setupFeaturesHandler(self, features_to_use):
        self.features_handler = FeaturesHandler.OnlineFeaturesHandler()
        self.features_handler.setup(features_to_use)
        return self.features_handler.getExtractionMethodNames()

    def collectSamples(self, features):
        return self.collector.handleSample(features)

    def resetCollectedSamples(self):
        self.collector.resetCollectedSamples()
