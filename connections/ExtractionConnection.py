__author__ = 'Anti'

from connections import NotebookConnection, ConnectionPostOfficeEnd
from generators import Extraction
import constants as c
import copy


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
        self.message_counter = 0

    def getConnection(self):
        return ExtractionMethodConnection()

    def getMethodResults(self, message, method_name):
        results = {}
        for tab in message:
            for method, sensors in message[tab]:
                if method == method_name:
                    if tab not in results:
                        results[tab] = message[tab][(method, sensors)]
                    break
        return results

    def getMaxResults(self, all_results):
        return {key: max(all_results[key].items(), key=lambda x: x[1]) for key in all_results}

    def getMaxFreqs(self, max_results):
        return {key: max_results[key][0] for key in max_results}

    def getMaxValues(self, max_results):
        return {key: max_results[key][1] for key in max_results}

    def getOverallMaxValue(self, max_values):
        return max(max_values.values()) if max_values != {} else None

    def getResults(self, all_results):
        max_results = self.getMaxResults(all_results)
        max_freqs = self.getMaxFreqs(max_results)
        max_values = self.getMaxValues(max_results)
        max_value = self.getOverallMaxValue(max_values)
        return all_results, max_freqs, max_values, max_value

    def getCcaResults(self, message):
        all_results = self.getMethodResults(message, c.CCA)
        return self.getResults(all_results)

    def getSumHarmonics(self, all_results):
        result = {}
        for tab in all_results:
            result[tab] = {}
            for freq in all_results[tab]:
                result[tab][freq] = sum(all_results[tab][freq].values())
        return result

    def getHarmonicsResults(self, all_results, harmonic):
        result = {}
        for tab in all_results:
            result[tab] = {}
            for freq in all_results[tab]:
                if harmonic in all_results[tab][freq]:
                    result[tab][freq] = copy.deepcopy(all_results[tab][freq][harmonic])
        return result

    def getMaxHarmonics(self, all_results):
        return {key: self.getMaxResults(all_results[key]) for key in all_results}

    def getHarmonics(self, all_results):
        result = []
        for tab in all_results:
            for freq in all_results[tab]:
                for harmonic in all_results[tab][freq]:
                    if harmonic not in result:
                        result.append(harmonic)
        return result

    def getSumPsdaResults(self, all_results):
        sum_harmonics = self.getSumHarmonics(all_results)
        harmonics = self.getHarmonics(all_results)
        max_harmonics = self.getMaxHarmonics(all_results)
        result = {harmonic: self.getResults(self.getHarmonicsResults(all_results, harmonic)) for harmonic in harmonics}
        result[c.RESULT_SUM] = self.getResults(sum_harmonics)
        return result

    def getSensors(self, message, method_name):
        result = []
        for tab in message:
            for method, sensors in message[tab]:
                if method == method_name:
                    for sensor in sensors:
                        if sensor not in result:
                            result.append(sensor)
        return result

    def getSensorResults(self, all_results, sensors):
        result = {}
        for tab in all_results:
            for sensor in all_results[tab]:
                if sensor == sensors:
                    result[tab] = all_results[tab][sensor]
        return result

    def getSumSensors(self, all_results):
        result = {}
        for tab in all_results:
            result[tab] = {}
            for sensor in all_results[tab]:
                for freq in all_results[tab][sensor]:
                    if freq not in result[tab]:
                        result[tab][freq] = copy.deepcopy(all_results[tab][sensor][freq])
                    else:
                        for harmonic in all_results[tab][sensor][freq]:
                            result[tab][freq][harmonic] += all_results[tab][sensor][freq][harmonic]
        return result

    def getPsdaResults(self, message):
        all_results = self.getMethodResults(message, c.PSDA)
        sum_sensors = self.getSumSensors(all_results)
        sensors = self.getSensors(message, c.PSDA)
        sensor_results = {sensor: self.getSensorResults(all_results, sensor) for sensor in sensors}
        result = {sensor: self.getSumPsdaResults(sensor_results[sensor]) for sensor in sensors}
        result[c.RESULT_SUM] = self.getSumPsdaResults(sum_sensors)
        return result

    def results(self, message):
        return {
            c.CCA: self.getCcaResults(copy.deepcopy(message)),
            c.SUM_PSDA: self.getSumPsdaResults(self.getMethodResults(copy.deepcopy(message), c.SUM_PSDA)),
            c.PSDA: self.getPsdaResults(copy.deepcopy(message))
        }

    def getMessages(self):
        message = self.receiveExtractionMessages()
        if message is not None:
            return self.results(message)


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
