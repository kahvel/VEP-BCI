from connections import ConnectionPostOfficeEnd, Connections
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
            new_connection.setup(dict_copy)
            new_connection.setId(tab_id)
            self.connections.append(new_connection)


class ExtractionMethodConnection(ExtractionConnection, Connections.MultipleConnections):
    def __init__(self):
        ExtractionConnection.__init__(self)
        Connections.MultipleConnections.__init__(self)

    def getConnection(self, method):
        if method == c.SUM_PSDA:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.SumPsda)
        elif method == c.CCA:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.Cca)
        elif method in (c.PSDA,):
            return ExtractionSensorConnection()
        else:
            raise ValueError("Illegal argument in getConnection: " + str(method))

    def setup(self, options):
        self.close()
        for method in options[c.DATA_EXTRACTION_METHODS]:
            new_connection = self.getConnection(method)
            dict_copy = copy.deepcopy(options)
            dict_copy[c.DATA_METHOD] = method
            new_connection.setup(dict_copy)
            new_connection.setId((method, tuple(options[c.DATA_EXTRACTION_SENSORS])))
            self.connections.append(new_connection)


class ExtractionSensorConnection(ExtractionConnection, Connections.MultipleConnections):
    def __init__(self):
        ExtractionConnection.__init__(self)
        Connections.MultipleConnections.__init__(self)

    def getConnection(self, method):
        if method == c.PSDA:
            return ConnectionPostOfficeEnd.ExtractionConnection(Extraction.Psda)
        else:
            raise ValueError("Illegal argument in getConnection: " + str(method))

    def setup(self, options):
        self.close()
        for sensor in options[c.DATA_EXTRACTION_SENSORS]:
            new_connection = self.getConnection(options[c.DATA_METHOD])
            dict_copy = copy.deepcopy(options)
            dict_copy[c.DATA_SENSORS] = [sensor]
            new_connection.setup(dict_copy)
            new_connection.setId(sensor)
            self.connections.append(new_connection)
