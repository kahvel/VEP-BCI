__author__ = 'Anti'

import Connections
import constants as c


class SensorConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)

    def setup(self, options):
        self.close()
        for sensor in options[c.DATA_SENSORS]:
            new_connection = self.getConnection(options[c.DATA_METHOD])
            options[c.DATA_SENSOR] = [sensor]
            new_connection.setup(options)
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
            options[c.DATA_METHOD] = method
            new_connection.setup(options)
            self.connections.append(new_connection)


class TabConnection(Connections.MultipleConnections):
    def __init__(self, options_key):
        Connections.MultipleConnections.__init__(self)
        self.options_key = options_key

    def setup(self, options):
        self.close()
        for option in options[self.options_key]:
            new_connection = self.getConnection()
            option[c.DATA_FREQS] = options[c.DATA_FREQS]
            new_connection.setup(option)
            self.connections.append(new_connection)

    def getConnection(self):
        raise NotImplementedError("getConnection not implemented!")