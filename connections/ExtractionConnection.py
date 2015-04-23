__author__ = 'Anti'

from connections import NotebookConnection, ConnectionPostOfficeEnd
import Extraction
import constants as c


class ExtractionTabConnection(NotebookConnection.TabConnection):
    def __init__(self):
        NotebookConnection.TabConnection.__init__(self, c.DATA_EXTRACTION)

    def getConnection(self):
        return ExtractionMethodConnection()


class ExtractionMethodConnection(NotebookConnection.MethodConnection):
    def __init__(self):
        NotebookConnection.MethodConnection.__init__(self)

    def getConnection(self, method):
        if method == c.SUM_PSDA:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.SumPsda)
        elif method in (c.PSDA, c.CCA):
            return ExtractionSensorConnection()
        else:
            raise ValueError("Illegal argument in getConnection: " + str(method))


class ExtractionSensorConnection(NotebookConnection.SensorConnection):
    def __init__(self):
        NotebookConnection.SensorConnection.__init__(self)

    def getConnection(self, method):
        if method == c.PSDA:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.Psda)
        elif method == c.CCA:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.Cca)
        else:
            raise ValueError("Illegal argument in getConnection: " + str(method))
