from connections.postoffice import ExtractionConnection, MyQueue
from generators.result.extraction import MessageHandler


class TrainingExtractionTabConnection(ExtractionConnection.ExtractionTabConnection):
    def __init__(self):
        ExtractionConnection.ExtractionTabConnection.__init__(self)

    def getConnection(self):
        return TrainingExtractionMethodConnection()


class TrainingExtractionMethodConnection(ExtractionConnection.ExtractionMethodConnection):
    def __init__(self):
        ExtractionConnection.ExtractionMethodConnection.__init__(self)

    def getSumPsda(self):
        return MyQueue.PostOfficeQueueConnection(MessageHandler.SumPsda)

    def getSnrPsda(self):
        return MyQueue.PostOfficeQueueConnection(MessageHandler.SnrPsda)

    def getCca(self):
        return MyQueue.PostOfficeQueueConnection(MessageHandler.CCA)

    def getLrt(self):
        return MyQueue.PostOfficeQueueConnection(MessageHandler.LRT)


class TrainingExtractionSensorConnection(ExtractionConnection.ExtractionSensorConnection):
    def __init__(self):
        ExtractionConnection.ExtractionSensorConnection.__init__(self)

    def getPsda(self):
        return MyQueue.PostOfficeQueueConnection(MessageHandler.SumPsda)
