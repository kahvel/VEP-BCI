from gui.widgets import OptionMenu, Buttons
from gui.widgets.frames import Frame
from gui.widgets.frames.notebooks import SameTabsNotebook
import constants as c
import Savable
import os


class RecordFrame(Frame.Frame, Savable.LoadableDirectory):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.RECORD_TAB_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenuFrame(self, c.TRAINING_RECORD, 0, 0, c.TRAINING_RECORD_NAMES),
            Buttons.Button(self, c.TRAINING_LOAD_EEG,  0, 1, command=self.loadEegClicked),
            SameTabsNotebook.ResultsNotebook(self, 1, 0, columnspan=3)
        ))

    def loadEegClicked(self):
        self.askLoadFile()

    def loadFromFile(self, directory):
        """
        askLoadFile calls this function when corresponding button is pressed.
        :param directory:
        :return:
        """
        self.sendEventToRoot(lambda x: x.loadEegEvent(directory), True)

    def saveEegEvent(self, directory):
        file = open(os.path.join(directory, "settings.txt"), "w")
        self.sendEventToRoot(lambda x: x.saveBciSettingsEvent(file))
