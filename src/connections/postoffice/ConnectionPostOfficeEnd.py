from connections import Connections
from connections.process import ConnectionProcessEnd
from gui_elements import TargetsWindow
from gui.main_window import MainWindow
from gui.training_window import TrainingWindow
from robot import MessageHandler

import OpenBCI


class PsychopyConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, TargetsWindow.TargetsWindow, ConnectionProcessEnd.PsychopyConnection)


class ExtractionConnection(Connections.Connection):
    def __init__(self, process):
        Connections.Connection.__init__(self, process, ConnectionProcessEnd.ExtractionConnection)

    def receiveExtractionMessages(self):
        return self.receiveMessageBlock()


class PlotConnection(Connections.Connection):
    def __init__(self, process):
        Connections.Connection.__init__(self, process, ConnectionProcessEnd.PlotConnection)


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
        Connections.Connection.__init__(self, OpenBCI.OpenBCI, ConnectionProcessEnd.EmotivConnection)


class RobotConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, MessageHandler.MessageHandler, ConnectionProcessEnd.RobotConnection)
        self.connection = self.newProcess()
