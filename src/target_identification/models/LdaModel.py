from target_identification.models import AbstractModel

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

import numpy as np


class TrainingLdaModel(AbstractModel.TrainingModel):
    def __init__(self):
        AbstractModel.TrainingModel.__init__(self)
        self.transformed_means = []

    def getModel(self):
        return LinearDiscriminantAnalysis()

    def fit(self, data, labels):
        self.model.fit(data, labels)
        self.transformed_means = np.dot(self.model.means_-self.model.xbar_, self.model.scalings_)

    def decisionFunction(self, data):
        # distances_to_means = map(lambda x: map(lambda y: np.linalg.norm(x-y), self.transformed_means), np.dot(data-self.model.xbar_, self.model.scalings_))
        # distances_to_means = map(lambda x: [-x[i]/(sum(x)-x[i]) for i in range(len(x))], distances_to_means)
        # return np.array(distances_to_means)
        return self.model.decision_function(data)  # value depends on the number of classes!


class OnlineLdaModel(AbstractModel.OnlineModel):
    def __init__(self):
        AbstractModel.OnlineModel.__init__(self)
        self.transformed_means = []

    def fit(self, data, labels):
        self.model.fit(data, labels)
        self.transformed_means = np.dot(self.model.means_-self.model.xbar_, self.model.scalings_)

    def decisionFunction(self, data):
        # distances_to_means = map(lambda x: map(lambda y: -np.linalg.norm(x-y), self.transformed_means), np.dot(data-self.model.xbar_, self.model.scalings_))
        # distances_to_means = map(lambda x: [-x[i]/(sum(x)-x[i]) for i in range(len(x))], distances_to_means)
        # return np.array(distances_to_means)
        return self.model.decision_function(data)  # value depends on the number of classes!
