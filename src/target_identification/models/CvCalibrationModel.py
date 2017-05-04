from sklearn.calibration import CalibratedClassifierCV
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC, SVC
from sklearn.neural_network import MLPClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.feature_selection import SelectFpr
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

    def moving_average(self, a, n) :
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def predictProba(self, data, n):
        # Normalisation
        normalised_probas = map(lambda probas: list(probas[i]/sum(probas) for i in range(len(probas))), self.model.predict_proba(data))
        return np.transpose(map(lambda x: self.moving_average(x, n), np.transpose(normalised_probas)))

        # old_pred = np.transpose(map(lambda x: self.moving_average(x, n), np.transpose(self.model.predict_proba(data))))
        # n = old_pred.shape[1]
        # return map(lambda probas: list(probas[i]-sum(probas[(i+j) % n] for j in range(1, n)) for i in range(n)), old_pred)

        # return np.transpose(map(lambda x: self.moving_average(x, n), np.transpose(self.model.predict_proba(data))))

    def splitThresholdPredict(self, scores, thresholds, margin):
        # thresholds
        # [[ 0.61298172  0.66761283  0.78342493] <- threshold for class 1, 2 and 3 (has to be larger than that)
        #  [ 0.38697659  0.06970417  0.22482575] <- class 1 is classified according to score of class 2 (has to be smaller than that) etc. First column is still class 1 threshold.
        #  [ 0.04919277  0.42939339  0.07072513]] <- class 1 is classified according to score of class 3 (has to be smaller than that) etc.
        predictions = []
        thresholds = np.transpose(thresholds)
        for sample_scores in scores:
            predicted = None
            for i, class_thresholds in enumerate(thresholds):
                if all(map(lambda (j, (s, t)): s >= t*(1+margin) if j == 0 else s < t*(1-margin), enumerate(zip(sample_scores, class_thresholds)))):
                # if sample_scores[0] > class_thresholds[0] or all(map(lambda (s, t): s < t*(1+margin), zip(sample_scores[1:], class_thresholds[1:]))):
                    predicted = i+1
                    break
            predictions.append(str(predicted))
        return predictions

    def thresholdPredict(self, scores, thresholds, margin):
        predictions = []
        for sample_scores in scores:
            predicted = None
            for i in range(len(sample_scores)):
                if all(map(lambda (j, (s, t)): s >= t*(1+margin) if i == j else s < t*(1-margin), enumerate(zip(sample_scores, thresholds)))):
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
        self.feature_selector = None
        self.do_feature_selection = None

    def setup(self, features_to_use, sample_count, recordings, matrix_builder_types):
        self.extraction_method_names = self.setupFeaturesHandler(features_to_use, recordings)
        self.setupScalingFunctions(self.extraction_method_names, recordings)
        self.feature_selector = SelectFpr(alpha=5e-2)
        self.model = OneVsRestClassifier(estimator=CalibratedClassifierCV(base_estimator=RandomForestClassifier(n_estimators=50, class_weight={1: 0.8, 0: 0.2}), cv=5))
        # self.model = CalibratedClassifierCV(base_estimator=RandomForestClassifier(n_estimators=50), cv=5)  # No OneVsOne
        # self.model = OneVsRestClassifier(estimator=RandomForestClassifier(n_estimators=50, class_weight={1: 0.8, 0: 0.2}))  # No CalibratedClassifierCV
        # self.model = OneVsRestClassifier(estimator=CalibratedClassifierCV(base_estimator=ExtraTreesClassifier(n_estimators=50, class_weight={1: 0.8, 0: 0.2}), cv=3))
        # self.model = OneVsRestClassifier(estimator=CalibratedClassifierCV(base_estimator=AdaBoostClassifier(base_estimator=DecisionTreeClassifier(class_weight={1: 0.8, 0: 0.2}, max_depth=2), n_estimators=50), cv=5))
        # self.model = OneVsRestClassifier(estimator=CalibratedClassifierCV(base_estimator=LinearDiscriminantAnalysis(), cv=5))
        # self.model = OneVsRestClassifier(estimator=CalibratedClassifierCV(base_estimator=LinearSVC(class_weight={1: 0.8, 0: 0.2}), cv=5))
        # self.model = OneVsRestClassifier(estimator=CalibratedClassifierCV(base_estimator=SVC(class_weight={1: 0.8, 0: 0.2}), cv=5))
        # self.model = OneVsRestClassifier(estimator=CalibratedClassifierCV(base_estimator=MLPClassifier(hidden_layer_sizes=(30,), max_iter=2000), cv=5))
        # self.model = CalibratedClassifierCV(base_estimator=RandomForestClassifier(max_depth=2, n_estimators=50), cv=5)
        # self.model = CalibratedClassifierCV(LinearDiscriminantAnalysis(), cv=5)
        self.collector = DataCollectors.TrainingCollector(sample_count)
        self.setupCollectorAndBuilder(sample_count, self.scaling_functions, self.extraction_method_names, matrix_builder_types)

    def fit(self, data, labels):
        self.feature_selector.fit(data, labels)
        # print self.feature_selector.get_support(True)
        print len(self.feature_selector.get_support(True))
        if len(self.feature_selector.get_support(True)) == 0:
            self.do_feature_selection = False
        else:
            self.do_feature_selection = True
        Model.fit(self, self.selectFeatures(data), labels)

    def selectFeatures(self, data):
        if self.do_feature_selection:
            return self.feature_selector.transform(data)
        else:
            return data

    def predict(self, data):
        return Model.predict(self, self.selectFeatures(data))

    def predictProba(self, data, n):
        return Model.predictProba(self, self.selectFeatures(data), n)

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
