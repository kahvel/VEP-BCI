from target_identification.models import AbstractModel

from sklearn.svm import SVC


class TrainingSvmModel(AbstractModel.TrainingModel):
    def __init__(self):
        AbstractModel.TrainingModel.__init__(self)

    def getModel(self):
        return SVC(decision_function_shape="ovr")

    def decisionFunction(self, data):
        return -self.model.decision_function(data)  # value depends on the number of classes!


class OnlineSvmModel(AbstractModel.OnlineModel):
    def __init__(self):
        AbstractModel.OnlineModel.__init__(self)

    def decisionFunction(self, data):
        return -self.model.decision_function(data)  # value depends on the number of classes!
