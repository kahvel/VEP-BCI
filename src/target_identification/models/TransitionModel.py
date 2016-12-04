from target_identification import DataCollectors
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
# from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
# from sklearn.svm import LinearSVC

import numpy as np


class Model(object):
    def __init__(self, use_proba):
        self.model = None
        self.use_proba = use_proba

    def setup(self, *args):
        raise NotImplementedError("setup not implemented!")

    def collectSamples(self, *args):
        raise NotImplementedError("collectSamples not implemented!")

    def getOrderedLabels(self):
        return self.model.classes_

    def fit(self, data, labels):
        self.model.fit(data, labels)

    def decisionFunction(self, data):
        return self.model.decision_function(data)

    def predictProba(self, data):
        return self.model.predict_proba(data)

    def predict(self, data):
        return self.model.predict(data)

    def getDecisionFunctionValues(self, data):
        """
        If use_proba=False then the function does not work with less than 3 classes.
        """
        return data
        if self.use_proba:
            return self.predictProba(data)
        else:
            return self.decisionFunction(data)

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


class TrainingModel(Model):
    def __init__(self, use_proba):
        Model.__init__(self, use_proba)
        self.features_to_use = None
        self.transition_collector = None
        self.self_transition_collector = None

    def getModel(self):
        # return LinearDiscriminantAnalysis()
        # return QuadraticDiscriminantAnalysis()
        # return LinearSVC()
        return RandomForestClassifier(n_estimators=1000, max_depth=3, min_samples_leaf=100, class_weight={'1': 0.1, '2': 0.1, '3': 0.1})#, 'transition': 0.8})
        # return AdaBoostClassifier(n_estimators=1000, learning_rate=0.5)
        # return GradientBoostingClassifier(n_estimators=1000, min_samples_leaf=500, max_depth=3)

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
        # self_transition_labels = map(str, self_transition_labels)
        # self_transition_labels = map(lambda x: "transition", self_transition_labels)
        # combined_data = np.concatenate((transitions, self_transitions), axis=0)
        # combined_labels = np.concatenate((transition_labels, self_transition_labels), axis=0)
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
    def __init__(self, use_proba):
        Model.__init__(self, use_proba)
        self.collector = None

    def setup(self, features_to_use, sample_count, model):
        self.model = model
        self.collector = DataCollectors.OnlineCollector(sample_count)

    def collectSamples(self, features):
        return self.collector.handleSample(features)

    def resetCollectedSamples(self):
        self.collector.resetCollectedSamples()
