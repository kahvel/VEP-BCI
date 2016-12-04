from target_identification.models import AbstractModel

from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis


class TrainingQdaModel(AbstractModel.TrainingModel):
    def __init__(self):
        AbstractModel.TrainingModel.__init__(self)

    def getModel(self):
        return QuadraticDiscriminantAnalysis()

    def decisionFunction(self, data):
        return self.model.decision_function(data)  # value depends on the number of classes!


class OnlineQdaModel(AbstractModel.OnlineModel):
    def __init__(self):
        AbstractModel.OnlineModel.__init__(self)

    def decisionFunction(self, data):
        return self.model.decision_function(data)  # value depends on the number of classes!
