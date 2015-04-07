__author__ = 'Anti'

import constants as c
import Connections


class Connection(Connections.AbstractConnection):
    def __init__(self, connection, name):
        Connections.AbstractConnection.__init__(self)
        self.connection = connection
        self.name = name

    def waitMessages(self, start_function, exit_function, update_function):  # wait for start or exit message
        while True:
            update_function()
            message = self.receiveMessagePoll(0.1)
            if message is not None:
                if message == c.START_MESSAGE:
                    print("Start " + self.name)
                    start_function()
                elif message == c.EXIT_MESSAGE:
                    print("Exit " + self.name)
                    exit_function()
                else:
                    print("Unknown message in " + self.name + ": " + message)

    def sendMessage(self, message):
        self.connection.send(message)

    def receiveMessage(self):
        return self.connection.recv()

    def closeConnection(self):
        self.sendMessage(c.CLOSE_MESSAGE)
        self.connection.close()


class PsychopyConnection(Connection):
    def __init__(self, connection):
        Connection.__init__(self, connection, c.CONNECTION_PSYCHOPY_NAME)

    def receiveCurrentTarget(self):
        if target != 0:
            self.sendMessage(target)

    def receiveOptions(self):
        return (
            self.receiveMessageBlock(),
            self.receiveMessageBlock(),
            self.receiveMessageBlock()
        )


class ExtractionConnection(Connection):
    def __init__(self, connection):
        Connection.__init__(self, connection, c.CONNECTION_EMOTIV_NAME)

    def sendOptions(self, options):
        for i, message in enumerate(options[c.DATA_EXTRACTION]):
            self.connections[i].sendMessage(message)
            self.connections[i].sendMessage(options[c.DATA_FREQS])


class PlotConnection(Connection):
    def __init__(self, connection):
        Connection.__init__(self, connection, c.CONNECTION_PLOT_NAME)

    def sendOptions(self, options):
        for i, message in enumerate(options[c.DATA_PLOTS]):
            self.connections[i].sendMessage(message)
            self.connections[i].sendMessage(options[c.DATA_FREQS])


class GameConnection(Connection):
    def __init__(self, connection):
        Connection.__init__(self, connection, c.CONNECTION_GAME_NAME)

    def sendOptions(self, options):
        self.connection.send(options[c.DATA_FREQS])


class MainConnection(Connection):
    def __init__(self, connection):
        Connection.__init__(self, connection, c.CONNECTION_MAIN_NAME)


class EmotivConnection(Connection):
    def __init__(self, connection):
        Connection.__init__(self, connection, c.CONNECTION_EMOTIV_NAME)