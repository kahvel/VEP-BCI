from sklearn.calibration import CalibratedClassifierCV
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.multiclass import OneVsRestClassifier
from target_identification import DataCollectors, ColumnsIterator, FeaturesHandler, MatrixBuilder, ScalingFunction

import numpy as np


class Model(ColumnsIterator.ColumnsIterator):
    def __init__(self):
        ColumnsIterator.ColumnsIterator.__init__(self)
        self.model = None
        self.labels = None
        self.matrix_builders = None
        self.extraction_method_names = None
        self.scaling_functions = None

    def fit(self, data, labels):
        self.model.fit(data, labels)

    def getOrderedLabels(self):
        return self.model.classes_

    def predict(self, data):
        return self.model.predict(data)

    def predictProba(self, data):
        return self.model.predict_proba(data)

    def thresholdPredict(self, data, thresholds, margin=0):
        predictions = []
        scores = self.model.predict_proba(data)
        for sample_scores in scores:
            predicted = None
            for i in range(len(sample_scores)):
                if all(map(lambda (j, (s, t)): s > t*(1+margin) if i == j else s < t*(1-margin), enumerate(zip(sample_scores, thresholds)))):
                    predicted = i+1
                    break
            predictions.append(str(predicted))
        return predictions

    def buildRatioMatrix(self, data):
        matrices = [builder.buildRatioMatrix(self.iterateColumns(data, self.extraction_method_names)) for builder in self.matrix_builders]
        return np.concatenate(matrices, axis=1)

    def getMinMax(self):
        return self.scaling_functions.minima, self.scaling_functions.maxima


class TrainingModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.features_to_use = None
        self.collector = None
        self.features_handler = None

    def setup(self, features_to_use, sample_count, recordings, matrix_builder_types):
        self.extraction_method_names = self.setupFeaturesHandler(features_to_use, recordings)
        self.setupScalingFunctions(self.extraction_method_names, recordings)
        self.model = OneVsRestClassifier(estimator=CalibratedClassifierCV(base_estimator=RandomForestClassifier(max_depth=3, n_estimators=50, class_weight={1: 0.8, 0: 0.2}), cv=5))
        # self.model = OneVsRestClassifier(estimator=CalibratedClassifierCV(base_estimator=AdaBoostClassifier(base_estimator=DecisionTreeClassifier(class_weight={1: 0.8, 0: 0.2}, max_depth=2), n_estimators=50), cv=5))
        # self.model = OneVsRestClassifier(estimator=CalibratedClassifierCV(base_estimator=LinearDiscriminantAnalysis(), cv=5))
        # self.model = CalibratedClassifierCV(base_estimator=RandomForestClassifier(max_depth=2, n_estimators=50), cv=5)
        # self.model = CalibratedClassifierCV(LinearDiscriminantAnalysis(), cv=5)
        self.collector = DataCollectors.TrainingCollector(sample_count)
        self.setupCollectorAndBuilder(sample_count, self.scaling_functions, self.extraction_method_names, matrix_builder_types)

    def setupScalingFunctions(self, extraction_method_names, recordings):
        self.scaling_functions = ScalingFunction.TrainingScalingFunctions()
        self.scaling_functions.setup(extraction_method_names, recordings)

    def setupCollectorAndBuilder(self, sample_count, scaling_functions, extraction_method_names, matrix_builder_types):
        self.collector = DataCollectors.TrainingCollector(sample_count)
        self.matrix_builders = []
        for type in matrix_builder_types:
            builder = MatrixBuilder.TrainingMatrixBuilder()
            builder.setup(scaling_functions, extraction_method_names, type)
            self.matrix_builders.append(builder)

    def setupFeaturesHandler(self, features_to_use, recordings):
        self.features_handler = FeaturesHandler.TrainingFeaturesHandler(recordings)
        self.features_handler.setup(features_to_use)
        self.features_to_use = self.features_handler.getUsedFeatures()
        return self.features_handler.getExtractionMethodNames()

    def collectSamples(self, features, labels):
        self.collector.reset()
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
        self.collector = None
        self.features_handler = None

    def setupFeaturesHandler(self, features_to_use):
        self.features_handler = FeaturesHandler.OnlineFeaturesHandler()
        self.features_handler.setup(features_to_use)
        return self.features_handler.getExtractionMethodNames()

    def setup(self, minimum, maximum, features_to_use, sample_count, model, matrix_builder_types):
        self.extraction_method_names = self.setupFeaturesHandler(features_to_use)
        self.setupScalingFunctions(minimum, maximum, self.extraction_method_names)
        self.model = model
        self.setupCollectorAndBuilder(sample_count, self.scaling_functions, self.extraction_method_names, matrix_builder_types)

    def setupScalingFunctions(self, minimum, maximum, extraction_method_names):
        self.scaling_functions = ScalingFunction.OnlineScalingFunctions()
        self.scaling_functions.setup(minimum, maximum, extraction_method_names)

    def setupCollectorAndBuilder(self, sample_count, scaling_functions, extraction_method_names, matrix_builder_types):
        self.collector = DataCollectors.OnlineCollector(sample_count)
        self.matrix_builders = []
        for type in matrix_builder_types:
            builder = MatrixBuilder.OnlineMatrixBuilder()
            builder.setup(scaling_functions, extraction_method_names, type)
            self.matrix_builders.append(builder)

    def collectSamples(self, features):
        return self.collector.handleSample(features)

    def resetCollectedSamples(self):
        self.collector.resetCollectedSamples()
