__author__ = 'Anti'

import constants as c
import Connections


class Connection(Connections.AbstractConnection):
    def __init__(self, connection, name):
        Connections.AbstractConnection.__init__(self)
        self.connection = connection
        self.name = name

    def waitMessages(self, start_function, exit_function, update_function, setup_function):  # wait messages
        message = None
        while True:
            update_function()
            if message is not None:
                if message == c.START_MESSAGE:
                    # print("Start", self.name)
                    message = start_function()
                    continue
                elif message == c.STOP_MESSAGE:
                    pass
                    # print("Stop", self.name)
                elif message == c.SETUP_MESSAGE:
                    self.sendMessage(setup_function())
                elif message == c.EXIT_MESSAGE:
                    # print("Exit", self.name)
                    exit_function()
                    return
                else:
                    print("Unknown message in " + self.name + ": " + str(message))
            message = self.receiveMessagePoll(0.1)

    def sendMessage(self, message):
        try:  # Without it some connections try to send message through closed pipe when exiting
            self.connection.send(message)
        except IOError, e:
            print(e)

    def receiveMessage(self):
        return self.connection.recv()

    def close(self):
        self.sendMessage(c.CLOSE_MESSAGE)
        self.connection.close()
        self.connection = None

    def receiveOptions(self):
        raise NotImplementedError("receiveOptions not implemented!")


class PsychopyConnection(Connection):
    def __init__(self, connection):
        Connection.__init__(self, connection, c.CONNECTION_PSYCHOPY_NAME)

    def receiveOptions(self):
        return self.receiveMessageBlock()


class ExtractionConnection(Connection):
    def __init__(self, connection):
        Connection.__init__(self, connection, c.CONNECTION_EXTRACTION_NAME)

    def receiveOptions(self):
        return self.receiveMessageBlock()


class PlotConnection(Connection):
    def __init__(self, connection):
        Connection.__init__(self, connection, c.CONNECTION_PLOT_NAME)

    def receiveOptions(self):
        return self.receiveMessageBlock()


class GameConnection(Connection):
    def __init__(self, connection):
        Connection.__init__(self, connection, c.CONNECTION_GAME_NAME)

    def sendOptions(self, options):
        self.connection.send(options[c.DATA_FREQS])


class MainConnection(Connection):
    def __init__(self, connection):
        Connection.__init__(self, connection, c.CONNECTION_MAIN_NAME)

    def sendMessage(self, message):
        self.connection.send(message)


class EmotivConnection(Connection):
    def __init__(self, connection):
        Connection.__init__(self, connection, c.CONNECTION_EMOTIV_NAME)