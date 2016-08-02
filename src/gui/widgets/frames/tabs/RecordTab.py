from gui.widgets import Buttons, OptionMenu
from gui.widgets.frames import Frame
import constants as c
import Savable


class RecordTab(Frame.Frame, Savable.Savable, Savable.Loadable):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.RECORD_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenu(self, c.TRAINING_RECORD,    0, 1, c.TRAINING_RECORD_NAMES),
            Buttons.Button       (self, c.TRAINING_SAVE_EEG,  1, 0, command=self.saveEegClicked),
            Buttons.Button       (self, c.TRAINING_LOAD_EEG,  1, 1, command=self.loadEegClicked),
            Buttons.Button       (self, c.TRAINING_RESET_EEG, 1, 2, command=self.resetEegClicked),
        ))

    def saveToFile(self, file):
        """
        askSaveFile calls this function when corresponding button is pressed.
        :param file:
        :return:
        """
        self.sendEventToRoot(lambda x: x.saveEegEvent(file))

    def loadFromFile(self, file):
        """
        askLoadFile calls this function when corresponding button is pressed.
        :param file:
        :return:
        """
        self.sendEventToRoot(lambda x: x.loadEegEvent(file))

    def saveEegClicked(self):
        self.askSaveFile()

    def loadEegClicked(self):
        self.askLoadFile()

    def resetEegClicked(self):
        self.sendEventToRoot(lambda x: x.resetEegEvent)
