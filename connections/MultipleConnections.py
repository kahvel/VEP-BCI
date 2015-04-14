__author__ = 'Anti'

import Connections
import constants as c


class SensorConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)

    # def sendOptions(self, *options_tuple):
    #     options, freqs = options_tuple
    #     for connection, sensor in zip(self.connections, options[c.DATA_SENSORS]):
    #         options[c.DATA_SENSOR] = sensor
    #         connection.sendOptions(options, freqs)

    def setup(self, sensors, options, target_freqs):
        self.close()
        for _ in sensors:
            self.addProcess(options[c.DATA_METHOD])
        for connection, sensor in zip(self.connections, sensors):
            options[c.DATA_SENSOR] = sensor
            connection.setup([sensor], options, target_freqs)

    def addProcess(self, method):
        raise NotImplementedError("addProcess not implemented!")


class MethodConnection(Connections.MultipleConnections):
    def __init__(self):
        Connections.MultipleConnections.__init__(self)

    # def sendOptions(self, *options_tuple):
    #     options, freqs = options_tuple
    #     for connection, method in zip(self.connections, options[c.DATA_METHODS]):
    #         options[c.DATA_METHOD] = method
    #         connection.sendOptions(options, freqs)

    def addProcess(self, method):
        raise NotImplementedError("addSumProcess not implemented!")

    def setup(self, methods, sensors, options, target_freqs):
        self.close()
        for method in methods:
            self.addProcess(method)
        for connection, method in zip(self.connections, options[c.DATA_METHODS]):
            options[c.DATA_METHOD] = method
            connection.setup(sensors, options, target_freqs)


class TabConnection(Connections.MultipleConnections):
    def __init__(self, options_key):
        Connections.MultipleConnections.__init__(self)
        self.options_key = options_key

    # def sendOptions(self, *options):
    #     options = options[0]
    #     for connection, option in zip(self.connections, options[self.options_key]):
    #         connection.sendOptions(option, options[c.DATA_FREQS])

    def setup(self, options):
        self.close()
        while len(self.connections) < len(options[self.options_key]):
            self.addProcess()
        for connection, option in zip(self.connections, options[self.options_key]):
            connection.setup(option[c.DATA_METHODS], option[c.DATA_SENSORS], option, options[c.DATA_FREQS])

    def addProcess(self):
        raise NotImplementedError("addProcess not implemented!")