from sklearn.isotonic import IsotonicRegression
from target_identification import DataCollectors

import numpy as np


class Models(object):
    def __init__(self):
        self.model = None
        self.labels = None

    def fit(self, data, labels):
        for i, column in enumerate(data.T):
            binary_labels = map(lambda x: x == str(i+1), labels)
            self.model[i].fit(column, binary_labels)
        self.labels = sorted(set(labels))

    def getOrderedLabels(self):
        return self.labels

    def getDecisionFunctionValues(self, data):
        return np.transpose([self.model[i].transform(column) for i, column in enumerate(data.T)])

    def predict(self, data):
        return map(lambda x: str(x+1), map(np.argmax, self.getDecisionFunctionValues(data)))

    def thresholdPredict(self, data, thresholds, margin=0):
        predictions = []
        scores = self.getDecisionFunctionValues(data)
        for sample_scores in scores:
            predicted = None
            for i in range(len(sample_scores)):
                if all(map(lambda (j, (s, t)): s > t*(1+margin) if i == j else s < t*(1-margin), enumerate(zip(sample_scores, thresholds)))):
                    predicted = i+1
                    break
            predictions.append(str(predicted))
        return predictions


class TrainingModel(Models):
    def __init__(self):
        Models.__init__(self)
        self.features_to_use = None
        self.transition_collector = None

    def getModel(self):
        return IsotonicRegression()

    def setup(self, features_to_use, sample_count):
        self.model = [self.getModel() for _ in range(3)]
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


class OnlineModel(Models):
    def __init__(self):
        Models.__init__(self)
        self.collector = None

    def setup(self, features_to_use, sample_count, model):
        self.model = model
        self.collector = DataCollectors.OnlineCollector(sample_count)

    def collectSamples(self, features):
        return self.collector.handleSample(features)

    def resetCollectedSamples(self):
        self.collector.resetCollectedSamples()
