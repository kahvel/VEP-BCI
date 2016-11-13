from target_identification import DataCollectors
from sklearn.ensemble import RandomForestClassifier

import numpy as np


class Model(object):
    def __init__(self):
        self.model = None

    def setup(self, *args):
        raise NotImplementedError("setup not implemented!")

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

    def predict(self, data):
        return self.model.predict(data)


class TrainingModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.features_to_use = None
        self.transition_collector = None
        self.self_transition_collector = None

    def getModel(self):
        return RandomForestClassifier(n_estimators=100, min_samples_leaf=10, max_depth=5)

    def setup(self, features_to_use, sample_count):
        self.model = self.getModel()
        self.transition_collector = DataCollectors.TrainingCollector(sample_count)
        self.self_transition_collector = DataCollectors.TransitionCollector(sample_count)

    def collectTransitions(self, features, labels):
        return self.transition_collector.combineSamples(features, labels)

    def collectSelfTransitions(self, features, labels):
        return self.self_transition_collector.combineSamples(features, labels)

    def collectSamples(self, features, labels):
        transitions, transition_labels = self.collectTransitions(features, labels)
        self_transitions, self_transition_labels = self.collectSelfTransitions(features, labels)
        self_transition_labels = map(str, self_transition_labels)
        combined_data = np.concatenate((transitions, self_transitions), axis=0)
        combined_labels = np.concatenate((transition_labels, self_transition_labels), axis=0)
        return transitions, transition_labels

    def getAllLookBackRatioMatrices(self, data, labels):
        self.transition_collector.reset()
        self.self_transition_collector.reset()
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
