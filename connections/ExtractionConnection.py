__author__ = 'Anti'

import MultipleConnections
import Extraction
import ConnectionPostOfficeEnd
import constants as c


class ExtractionTabConnection(MultipleConnections.TabConnection):
    def __init__(self):
        MultipleConnections.TabConnection.__init__(self, c.DATA_EXTRACTION)

    def addProcess(self):
        self.connections.append(ExtractionMethodConnection())


class ExtractionMethodConnection(MultipleConnections.MethodConnection):
    def __init__(self):
        MultipleConnections.MethodConnection.__init__(self)

    def isSumChannel(self, method):
        return method == c.SUM_PSDA or method == c.SUM_BOTH

    def addProcess(self, method):
        if method == c.SUM_PSDA:
            self.connections.append(ConnectionPostOfficeEnd.ExtractionConnection(Extraction.SumPsdaExtraction))
        elif method == c.SUM_BOTH:
            self.connections.append(ConnectionPostOfficeEnd.ExtractionConnection(Extraction.SumCcaPsdaExtraction))
        elif method == c.PSDA:
            self.connections.append(ConnectionPostOfficeEnd.ExtractionConnection(Extraction.NotSumPsdaExtraction))
        elif method == c.BOTH:
            self.connections.append(ConnectionPostOfficeEnd.ExtractionConnection(Extraction.NotSumCcaPsdaExtraction))
        elif method == c.CCA:
            self.connections.append(ConnectionPostOfficeEnd.ExtractionConnection(Extraction.NotSumCcaExtraction))
