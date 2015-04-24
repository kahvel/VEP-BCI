__author__ = 'Anti'

import Connections
import constants as c
import copy


class SensorConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)

    def setup(self, options):
        self.close()
        for sensor in options[c.DATA_SENSORS]:
            new_connection = self.getConnection(options[c.DATA_METHOD])
            dict_copy = copy.deepcopy(options)
            dict_copy[c.DATA_SENSORS] = [sensor]
            new_connection.setup(dict_copy)
            self.connections.append(new_connection)

    def getConnection(self, method):
        raise NotImplementedError("getConnection not implemented!")


class MethodConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)

    def getConnection(self, method):
        raise NotImplementedError("getConnection not implemented!")

    def setup(self, options):
        self.close()
        for method in options[c.DATA_METHODS]:
            new_connection = self.getConnection(method)
            dict_copy = copy.deepcopy(options)
            dict_copy[c.DATA_METHOD] = method
            new_connection.setup(dict_copy)
            self.connections.append(new_connection)


class TabConnection(Connections.MultipleConnections):
    def __init__(self, options_key):
        Connections.MultipleConnections.__init__(self)
        self.options_key = options_key

    def setup(self, options):
        self.close()
        for option in options[self.options_key]:
            new_connection = self.getConnection()
            dict_copy = copy.deepcopy(option)
            dict_copy[c.DATA_FREQS] = options[c.DATA_FREQS]
            new_connection.setup(dict_copy)
            self.connections.append(new_connection)

    def getConnection(self):
        raise NotImplementedError("getConnection not implemented!")