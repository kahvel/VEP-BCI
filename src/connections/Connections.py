__author__ = 'Anti'

import constants as c
import multiprocessing


class AbstractConnection(object):
    def __init__(self):
        self.connection = None
        self.id = None

    def sendMessage(self, message):
        raise NotImplementedError("sendMessage not implemented!")

    def receiveMessage(self):
        raise NotImplementedError("receiveMessage not implemented!")

    def sendOptions(self, *options):
        raise NotImplementedError("sendOptions not implemented!")

    def setupSuccessful(self):
        raise NotImplementedError("setupSuccessful not implemented!")

    def isClosed(self):
        raise NotImplementedError("isClosed not implemented!")

    def close(self):
        raise NotImplementedError("close not implemented!")

    def sendStartMessage(self):
        self.sendMessage(c.START_MESSAGE)

    def sendStopMessage(self):
        self.sendMessage(c.STOP_MESSAGE)

    def sendExitMessage(self):
        self.sendMessage(c.EXIT_MESSAGE)

    def sendSetupMessage(self):
        self.sendMessage(c.SETUP_MESSAGE)

    def receiveMessageInstant(self):
        if self.connection is not None:
            if self.connection.poll():  # If no timeout, returns immediately. If None, timeout is infinite.
                return self.receiveMessage()

    def receiveMessagePoll(self, timeout):
        if self.connection is not None:
            if self.connection.poll(timeout):
                return self.receiveMessage()

    def receiveMessageBlock(self):
        if self.connection is not None:
            if self.connection.poll(None):
                return self.receiveMessage()
            else:
                print("Warning! Infinite poll returned False.")

    def setId(self, id):
        self.id = id


class Connection(AbstractConnection):
    def __init__(self, process, connection_other_end):
        AbstractConnection.__init__(self)
        self.process = process
        self.connection_other_end = connection_other_end

    def sendMessage(self, message):
        self.connection.send(message)

    def receiveMessage(self):
        return self.connection.recv()

    def setup(self, *options):
        if self.connection is None:
            self.connection = self.newProcess()
        self.sendOptions(*options)

    def newProcess(self):
        from_process, to_process = multiprocessing.Pipe()
        multiprocessing.Process(target=self.process, args=(self.connection_other_end(from_process),)).start()
        return to_process

    def isClosed(self):
        return self.connection is None

    def setupSuccessful(self):
        while True:
            message = self.receiveMessageBlock()
            if message == c.SUCCESS_MESSAGE:
                return True
            elif message == c.FAIL_MESSAGE:
                return False
            else:
                print("Connection.setupSuccessful: " + str(message))

    def close(self):
        self.sendExitMessage()
        self.receiveMessageBlock()
        self.connection = None

    def getRunFunction(self, connection):
        raise NotImplementedError("getRunFunction not implemented!")

    def getOtherEndInstance(self, connection):
        raise NotImplementedError("getOtherEndInstance not implemented!")


class MultipleConnections(AbstractConnection):
    def __init__(self):
        AbstractConnection.__init__(self)
        self.connections = []
        """ @type : list[Connection] """

    def sendMessage(self, message):
        for connection in self.connections:
            connection.sendMessage(message)

    def receiveMessageInstant(self):
        return [connection.receiveMessageInstant() for connection in self.connections]

    def receiveMessagePoll(self, timeout):
        return [connection.receiveMessagePoll(timeout) for connection in self.connections]

    def receiveMessageBlock(self):
        return [connection.receiveMessageBlock() for connection in self.connections]

    def close(self, arg=None):
        connections = arg if arg is not None else self.connections
        for i in range(len(connections)-1, -1, -1):
            connections[i].close()
            del connections[i]

    def setupSuccessful(self):
        for connection in self.connections:
            if not connection.setupSuccessful():
                return False
        return True

    def isClosed(self):
        return all(connection.isClosed() for connection in self.connections)
