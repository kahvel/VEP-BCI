__author__ = 'Anti'

from connections import NotebookConnection, ConnectionPostOfficeEnd, Connections
import Extraction
import constants as c
import copy


class ExtractionMasterConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)

    def setup(self, options):
        self.close()
        options2 = copy.deepcopy(options)
        for option in options2[c.DATA_EXTRACTION]:
            option[c.DATA_OPTIONS][c.OPTIONS_LENGTH] /= 2
        new_connection = ExtractionTabConnection()
        new_connection.setup(options)
        self.connections.append(new_connection)
        new_connection = ExtractionTabConnection()
        new_connection.setup(options2)
        self.connections.append(new_connection)


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
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.SumPsdaExtraction)
        elif method == c.SUM_BOTH:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.SumCcaPsdaExtraction)
        elif method == c.PSDA:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.NotSumPsdaExtraction)
        elif method == c.BOTH:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.NotSumCcaPsdaExtraction)
        elif method == c.CCA:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.NotSumCcaExtraction)
