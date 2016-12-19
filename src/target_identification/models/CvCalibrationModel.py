from sklearn.calibration import CalibratedClassifierCV
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from target_identification import DataCollectors

import numpy as np


class Model(object):
    def __init__(self):
        self.model = None
        self.labels = None

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


class TrainingModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.features_to_use = None
        self.transition_collector = None

    def setup(self, features_to_use, sample_count):
        self.model = CalibratedClassifierCV(base_estimator=RandomForestClassifier(max_depth=2, n_estimators=50), cv=5)
        # self.model = CalibratedClassifierCV(LinearDiscriminantAnalysis(), cv=5)
        self.transition_collector = DataCollectors.TrainingCollector(sample_count)

    def collectTransitions(self, features, labels):
        return self.transition_collector.combineSamples(features, labels)

    def collectSamples(self, features, labels):
        transitions, transition_labels = self.collectTransitions(features, labels)
        return transitions, transition_labels

    def getAllLookBackRatioMatrices(self, data, labels):
        self.transition_collector.reset()
        all_matrices = []
        all_labels = []
        for current_data, current_labels in zip(data, labels):
            combined_data, combined_labels = self.collectSamples(current_data, current_labels)
            all_matrices.append(combined_data)
            all_labels.append(combined_labels)
        return all_matrices, all_labels

    def getConcatenatedMatrix(self, data, labels):
        matrices, labels = self.getAllLookBackRatioMatrices(data, labels)
        data_matrix = np.concatenate(matrices, axis=0)
        data_labels = np.concatenate(labels, axis=0)
        return data_matrix, data_labels


class OnlineModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.collector = None

    def setup(self, features_to_use, sample_count, model):
        self.model = model
        self.collector = DataCollectors.OnlineCollector(sample_count)

    def collectSamples(self, features):
        return self.collector.handleSample(features)

    def resetCollectedSamples(self):
        self.collector.resetCollectedSamples()
