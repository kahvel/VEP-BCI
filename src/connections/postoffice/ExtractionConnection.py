import copy

from connections import Connections
from connections.postoffice import ConnectionPostOfficeEnd, MyQueue
from generators.result.extraction import Extraction
import constants as c


class ExtractionConnection(object):
    def receiveExtractionMessages(self):
        result = {}
        for connection in self.connections:
            message = connection.receiveExtractionMessages()
            if message is not None:
                result[connection.id] = message
        return result if result != {} else None


class ExtractionTabConnection(ExtractionConnection, Connections.MultipleConnections):
    def __init__(self):
        ExtractionConnection.__init__(self)
        Connections.MultipleConnections.__init__(self)

    def getConnection(self):
        return ExtractionMethodConnection()

    def getMessages(self):
        message = self.receiveExtractionMessages()
        if message is not None:
            return message

    def setup(self, options):
        self.close()
        for tab_id, tab_options in options[c.DATA_EXTRACTION].items():
            new_connection = self.getConnection()
            dict_copy = copy.deepcopy(tab_options)
            dict_copy[c.DATA_FREQS] = tab_options[c.DATA_EXTRACTION_TARGETS]
            dict_copy[c.DATA_HARMONICS] = options[c.DATA_HARMONICS][tab_id]
            dict_copy[c.DATA_PROCESS_SHORT_SIGNAL] = options[c.DATA_PROCESS_SHORT_SIGNAL]
            new_connection.setup(dict_copy)
            new_connection.setId(tab_id)
            self.connections.append(new_connection)


class TrainingExtractionTabConnection(ExtractionTabConnection):
    def __init__(self):
        ExtractionTabConnection.__init__(self)

    def getConnection(self):
        return TrainingExtractionMethodConnection()


class ExtractionMethodConnection(ExtractionConnection, Connections.MultipleConnections):
    def __init__(self):
        ExtractionConnection.__init__(self)
        Connections.MultipleConnections.__init__(self)

    def getConnection(self, method):
        if method == c.SUM_PSDA:
            return self.getSumPsda()
        elif method == c.CCA:
            return self.getCca()
        elif method in (c.PSDA,):
            return ExtractionSensorConnection()
        else:
            raise ValueError("Illegal argument in getConnection: " + str(method))

    def getSumPsda(self):
        return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.SumPsda)

    def getCca(self):
        return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.Cca)

    def setup(self, options):
        self.close()
        for method in options[c.DATA_EXTRACTION_METHODS]:
            new_connection = self.getConnection(method)
            dict_copy = copy.deepcopy(options)
            dict_copy[c.DATA_METHOD] = method
            new_connection.setup(dict_copy)
            new_connection.setId((method, tuple(options[c.DATA_EXTRACTION_SENSORS])))
            self.connections.append(new_connection)


class TrainingExtractionMethodConnection(ExtractionMethodConnection):
    def __init__(self):
        ExtractionMethodConnection.__init__(self)

    def getSumPsda(self):
        return MyQueue.PostOfficeQueueConnection(Extraction.SumPsda)

    def getCca(self):
        return MyQueue.PostOfficeQueueConnection(Extraction.Cca)


class ExtractionSensorConnection(ExtractionConnection, Connections.MultipleConnections):
    def __init__(self):
        ExtractionConnection.__init__(self)
        Connections.MultipleConnections.__init__(self)

    def getConnection(self, method):
        if method == c.PSDA:
            return self.getPsda()
        else:
            raise ValueError("Illegal argument in getConnection: " + str(method))

    def getPsda(self):
        return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.Psda)

    def setup(self, options):
        self.close()
        for sensor in options[c.DATA_EXTRACTION_SENSORS]:
            new_connection = self.getConnection(options[c.DATA_METHOD])
            dict_copy = copy.deepcopy(options)
            dict_copy[c.DATA_SENSORS] = [sensor]
            new_connection.setup(dict_copy)
            new_connection.setId(sensor)
            self.connections.append(new_connection)


class TrainingExtractionSensorConnection(ExtractionSensorConnection):
    def __init__(self):
        ExtractionSensorConnection.__init__(self)

    def getPsda(self):
        return MyQueue.PostOfficeQueueConnection(Extraction.SumPsda)
