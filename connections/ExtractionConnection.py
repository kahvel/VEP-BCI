__author__ = 'Anti'

from connections import NotebookConnection, ConnectionPostOfficeEnd
from generators import Extraction
import constants as c


class ExtractionTabConnection(NotebookConnection.TabConnection):
    def __init__(self):
        NotebookConnection.TabConnection.__init__(self, c.DATA_EXTRACTION)

    def getConnection(self):
        return ExtractionMethodConnection()

    def addFrequency(self, results, message):
        if message is not None:
            name, freq = message
            results[name] = freq

    def getDetailedResults(self, message):
        results = {}
        for i, tab in enumerate(message):
            i += 1
            results[i] = {}
            for method in tab:
                if isinstance(method, list):
                    for sensor in method:
                        self.addFrequency(results[i], sensor)
                else:
                    self.addFrequency(results[i], method)
        return results

    def addToDict(self, dict, value):
        if value in dict:
            dict[value] += 1
        else:
            dict[value] = 1

    def getTabResults(self, detailed_results):
        tab_results = {}
        for tab in detailed_results:
            tab_results[tab] = {}
            for method in detailed_results[tab]:
                self.addToDict(tab_results[tab], detailed_results[tab][method])
        return tab_results

    def getMethodResults(self, detailed_results):
        method_results = {}
        for tab in detailed_results:
            for method in detailed_results[tab]:
                if method not in method_results:
                    method_results[method] = {}
                self.addToDict(method_results[method], detailed_results[tab][method])
        return method_results

    def getResults(self, detailed_results):
        results = {}
        for tab in detailed_results:
            for method in detailed_results[tab]:
                self.addToDict(results, detailed_results[tab][method])
        return results

    def getMessages(self):
        message = self.receiveExtractionMessages()
        print(message)
        return {}, {}, {}, {}, {}
        # detailed_results = self.getDetailedResults(message)
        # tab_results = self.getTabResults(detailed_results)
        # method_results = self.getMethodResults(detailed_results)
        # results = self.getResults(detailed_results)
        # result_count = sum(results.itervalues())
        # return result_count, results, tab_results, method_results, detailed_results

    def receiveExtractionMessages(self):
        return {connection.id: connection.receiveExtractionMessages() for connection in self.connections}


class ExtractionMethodConnection(NotebookConnection.MethodConnection):
    def __init__(self):
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

    def receiveExtractionMessages(self):
        return {connection.id: connection.receiveExtractionMessages() for connection in self.connections}


class ExtractionSensorConnection(NotebookConnection.SensorConnection):
    def __init__(self):
        NotebookConnection.SensorConnection.__init__(self)

    def getConnection(self, method):
        if method == c.PSDA:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.Psda)
        else:
            raise ValueError("Illegal argument in getConnection: " + str(method))

    def receiveExtractionMessages(self):
        return {connection.id: connection.receiveExtractionMessages() for connection in self.connections}
