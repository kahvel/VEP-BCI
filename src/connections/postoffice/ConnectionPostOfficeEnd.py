from connections import Connections
from connections.process import ConnectionProcessEnd
from gui_elements import TargetsWindow
from gui.main_window import MainWindow
from gui.training_window import TrainingWindow

import MyEmotiv
import Robot


class PsychopyConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, TargetsWindow.TargetsWindow, ConnectionProcessEnd.PsychopyConnection)
        self.connection = self.newProcess()

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


class TrainingConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, TrainingWindow.TrainingWindow, ConnectionProcessEnd.MainConnection)
        self.connection = self.newProcess()


class EmotivConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, MyEmotiv.MyEmotiv, ConnectionProcessEnd.EmotivConnection)
        self.connection = self.newProcess()

    def sendOptions(self, *options):
        self.sendSetupMessage()


class RobotConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, Robot.Robot, ConnectionProcessEnd.RobotConnection)
        self.connection = self.newProcess()

    def sendOptions(self, options):
        self.sendSetupMessage()
        self.sendMessage(options)
