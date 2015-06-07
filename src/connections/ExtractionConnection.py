import copy

from connections import NotebookConnection, ConnectionPostOfficeEnd
from generators import Extraction
import constants as c


class ExtractionConnection(object):
    def receiveExtractionMessages(self):
        result = {}
        for connection in self.connections:
            message = connection.receiveExtractionMessages()
            if message is not None:
                result[connection.id] = message
        return result if result != {} else None


class ExtractionTabConnection(ExtractionConnection, NotebookConnection.TabConnection):
    def __init__(self):
        ExtractionConnection.__init__(self)
        NotebookConnection.TabConnection.__init__(self, c.DATA_EXTRACTION)

    def getConnection(self):
        return ExtractionMethodConnection()

    def getMessages(self):
        message = self.receiveExtractionMessages()
        if message is not None:
            return message


class ExtractionMethodConnection(ExtractionConnection, NotebookConnection.MethodConnection):
    def __init__(self):
        ExtractionConnection.__init__(self)
        NotebookConnection.MethodConnection.__init__(self)

    def getConnection(self, method):
        if method == c.SUM_PSDA:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.SumPsda)
        elif method == c.CCA:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.Cca)
        elif method in (c.PSDA,):
            return ExtractionSensorConnection()
        else:
            raise ValueError("Illegal argument in getConnection: " + str(method))


class ExtractionSensorConnection(ExtractionConnection, NotebookConnection.SensorConnection):
    def __init__(self):
        ExtractionConnection.__init__(self)
        NotebookConnection.SensorConnection.__init__(self)

    def getConnection(self, method):
        if method == c.PSDA:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.Psda)
        else:
            raise ValueError("Illegal argument in getConnection: " + str(method))
