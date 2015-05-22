from gui import TargetsWindow
from gui.main_window import MainWindow

__author__ = 'Anti'

import Connections
import ConnectionProcessEnd
import MyEmotiv


class PsychopyConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, TargetsWindow.TargetsWindow, ConnectionProcessEnd.PsychopyConnection)

    def sendOptions(self, options):
        self.sendSetupMessage()
        self.connection.send(options)


class ExtractionConnection(Connections.Connection):
    def __init__(self, process):
        Connections.Connection.__init__(self, process, ConnectionProcessEnd.ExtractionConnection)

    def sendOptions(self, options):
        self.sendSetupMessage()
        self.connection.send(options)

    def receiveExtractionMessages(self):
        return self.receiveMessageBlock()


class PlotConnection(Connections.Connection):
    def __init__(self, process):
        Connections.Connection.__init__(self, process, ConnectionProcessEnd.PlotConnection)

    def sendOptions(self, options):
        self.sendSetupMessage()
        self.sendMessage(options)


class MainConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, MainWindow.MainWindow, ConnectionProcessEnd.MainConnection)
        self.connection = self.newProcess()


class EmotivConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, MyEmotiv.MyEmotiv, ConnectionProcessEnd.EmotivConnection)
        self.connection = self.newProcess()

    def sendOptions(self, *options):
        self.sendSetupMessage()