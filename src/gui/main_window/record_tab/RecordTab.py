import os

from gui_elements.widgets import OptionMenu, Buttons
from gui_elements.widgets.frames import Frame
import RecordNotebook
import constants as c
import Savable


class RecordTab(Frame.Frame, Savable.LoadableDirectory, Savable.SavableDirectory):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_NOTEBOOK_RECORD_TAB, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenuFrame(self, c.TRAINING_RECORD, 0, 0, c.TRAINING_RECORD_NAMES),
            Buttons.Button(self, c.RECORDING_LOAD_TABS,  0, 1, command=self.loadEegClicked),
            Buttons.Button(self, c.RECORDING_SAVE_TABS,  0, 2, command=self.saveEegClicked),
            RecordNotebook.RecordNotebook(self, 1, 0, columnspan=3)
        ))

    def loadEegClicked(self):
        self.askLoadFile()

    def saveEegClicked(self):
        self.askSaveFile()

    def saveToFile(self, directory):
        """
        askSaveFile calls this function when corresponding button is pressed.
        :param directory:
        :return:
        """
        self.sendEventToChildrenWithIndex(lambda x, y: x.saveAllTabsEvent(directory, y), None)

    def loadFromFile(self, directory):
        """
        askLoadFile calls this function when corresponding button is pressed.
        :param directory:
        :return:
        """
        self.sendEventToAll(lambda x: x.loadEegEvent(directory), True)

    def saveSettings(self, directory):
        file = open(os.path.join(directory, "settings.txt"), "w")
        self.sendEventToAll(lambda x: x.saveBciSettingsEvent(file))

    def saveEegEvent(self, directory):
        self.saveSettings(directory)

    def saveAllTabsEvent(self, directory, i):
        self.saveSettings(directory)
