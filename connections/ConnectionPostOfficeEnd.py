__author__ = 'Anti'

import Connections
import constants as c
import ConnectionProcessEnd
import TargetsWindow
import MyEmotiv
import Game
from main_window import MainWindow


class PsychopyConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, TargetsWindow.TargetsWindow, ConnectionProcessEnd.PsychopyConnection)

    def sendOptions(self, options):
        self.sendSetupMessage()
        self.connection.send(options[c.DATA_BACKGROUND])
        self.connection.send(options[c.DATA_TARGETS])
        self.connection.send(options[c.DATA_TEST][c.TEST_STANDBY])

    def sendCurrentTarget(self, target):
        if target != 0:
            self.sendMessage(target)


class ExtractionConnection(Connections.Connection):
    def __init__(self, process):
        Connections.Connection.__init__(self, process, ConnectionProcessEnd.ExtractionConnection)

    def sendOptions(self, sensors, options, target_freqs):
        self.sendSetupMessage()
        self.connection.send((sensors, options, target_freqs))


class PlotConnection(Connections.Connection):
    def __init__(self, process):
        Connections.Connection.__init__(self, process, ConnectionProcessEnd.PlotConnection)

    def sendOptions(self, sensors, options, target_freqs):
        self.sendSetupMessage()
        self.sendMessage((sensors, options, target_freqs))


class GameConnection(Connections.Connection):
    def __init__(self):
        Connections.Connection.__init__(self, Game.Game, ConnectionProcessEnd.GameConnection)

    def sendOptions(self, options):
        self.connection.send(options[c.DATA_FREQS])


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