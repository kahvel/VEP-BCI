__author__ = 'Anti'

import multiprocessing
import constants as c


class AbstractConnection(object):
    def __init__(self, function):
        self.func = function

    def newProcess(self):
        from_process, to_process = multiprocessing.Pipe()
        multiprocessing.Process(target=self.func, args=(from_process,)).start()
        return to_process

    def sendMessage(self, message):
        raise NotImplementedError("sendMessage not implemented!")

    def sendStartMessage(self):
        self.sendMessage(c.START_MESSAGE)

    def sendStopMessage(self):
        self.sendMessage(c.STOP_MESSAGE)

    def sendOptions(self, options):
        pass

    def addConnections(self, n):
        raise NotImplementedError("addConnections not implemented!")

    def getMessage(self, function):
        raise NotImplementedError("getMessage not implemented!")


class SingleConnection(AbstractConnection):
    def __init__(self, function, make_process=False):
        AbstractConnection.__init__(self, function)
        self.connection = self.newProcess() if make_process else None

    def sendMessage(self, message):
        self.connection.send(message)

    def receiveMessageInstant(self):
        if self.connection.poll():  # If no timeout, returns immediately. If None, timeout is infinite.
            return self.connection.recv()

    def receiveMessagePoll(self, timeout):
        if self.connection.poll(timeout):
            return self.connection.recv()

    def receiveMessageBlock(self):
        if self.connection.poll(None):
            return self.connection.recv()
        else:
            print("Warning! Infinite poll returned False.")

    def addConnections(self, n):
        if self.connection is None:
            self.connection = self.newProcess()

    def getMessageInstant(self):
        return self.getMessage(self.receiveMessageInstant)

    def getMessageBlock(self):
        return self.getMessage(self.receiveMessageBlock)

    def getMessage(self, function):
        message = function()
        if message == c.CLOSE_MESSAGE:
            self.connection.close()
            self.connection = None
        else:
            return message


class MultipleConnections(AbstractConnection):
    def __init__(self, function):
        AbstractConnection.__init__(self, function)
        self.connections = []
        """ @type : list[SingleConnection] """
        self.options_key = None

    def sendMessage(self, message):
        for connection in self.connections:
            connection.sendMessage(message)

    def addProcess(self):
        self.connections.append(SingleConnection(self.func, make_process=True))

    def addConnections(self, n):
        while len(self.connections) < n:
            self.addProcess()

    def getMessageInstant(self):
        return self.getMessage(lambda x: x.getMessageInstant())

    def getMessageBlock(self):
        return self.getMessage(lambda x: x.getMessageBlock())

    def getMessage(self, function):
        messages = []
        for i in range(len(self.connections)-1, -1, -1):
            message = function(self.connections[i])
            if message is not None:
                messages.append(message)
            elif self.connections[i] is None:  # If connection is None, it was closed by function(self.connections[i])
                del self.connections[i]
        return messages


class PsychopyConnection(SingleConnection):
    def __init__(self, function):
        SingleConnection.__init__(self, function)

    def sendOptions(self, options):
        self.connection.send(options[c.DATA_BACKGROUND])
        self.connection.send(options[c.DATA_TARGETS])
        self.connection.send(options[c.DATA_TEST][c.TEST_STANDBY])

    def sendCurrentTarget(self, target):
        if target != 0:
            self.sendMessage(target)


class ExtractionConnection(MultipleConnections):
    def __init__(self, function):
        MultipleConnections.__init__(self, function)

    def sendOptions(self, options):
        for i, message in enumerate(options[c.DATA_EXTRACTION]):
            self.connections[i].sendMessage(message)
            self.connections[i].sendMessage(options[c.DATA_FREQS])


class PlotConnection(MultipleConnections):
    def __init__(self, function):
        MultipleConnections.__init__(self, function)

    def sendOptions(self, options):
        for i, message in enumerate(options[c.DATA_PLOTS]):
            self.connections[i].sendMessage(message)
            self.connections[i].sendMessage(options[c.DATA_FREQS])


class GameConnection(SingleConnection):
    def __init__(self, function):
        SingleConnection.__init__(self, function)

    def sendOptions(self, options):
        self.connection.send(options[c.DATA_FREQS])


class MainConnection(SingleConnection):
    def __init__(self, function):
        SingleConnection.__init__(self, function)
        self.connection = self.newProcess()


class EmotivConnection(SingleConnection):
    def __init__(self, function):
        SingleConnection.__init__(self, function)
        self.connection = self.newProcess()
