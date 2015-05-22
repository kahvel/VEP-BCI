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
            new_connection.setId(sensor)
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
            new_connection.setId((method, tuple(options[c.DATA_SENSORS])))
            self.connections.append(new_connection)


class TabConnection(Connections.MultipleConnections):
    def __init__(self, options_key):
        Connections.MultipleConnections.__init__(self)
        self.options_key = options_key

    def setup(self, options):
        self.close()
        for tab_id, option in enumerate(options[self.options_key]):
            new_connection = self.getConnection()
            dict_copy = copy.deepcopy(option)
            dict_copy[c.DATA_FREQS] = options[c.DATA_FREQS]
            dict_copy[c.DATA_HARMONICS] = options[c.DATA_HARMONICS]
            new_connection.setup(dict_copy)
            new_connection.setId(tab_id+1)
            self.connections.append(new_connection)

    def getConnection(self):
        raise NotImplementedError("getConnection not implemented!")