from target_identification.models import AbstractModel

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis


class TrainingLdaModel(AbstractModel.TrainingModel):
    def __init__(self):
        AbstractModel.TrainingModel.__init__(self)

    def getModel(self):
        return LinearDiscriminantAnalysis()

    def decisionFunction(self, data):
        return self.model.decision_function(data)  # value depends on the number of classes!


class OnlineLdaModel(AbstractModel.OnlineModel):
    def __init__(self):
        AbstractModel.OnlineModel.__init__(self)

    def decisionFunction(self, data):
        return self.model.decision_function(data)  # value depends on the number of classes!
