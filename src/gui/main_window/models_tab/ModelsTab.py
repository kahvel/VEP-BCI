from gui_elements.widgets import Buttons
from gui_elements.widgets.frames import Frame
import ModelsNotebook
import constants as c
import Savable

import os


class ModelsTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_NOTEBOOK_MODELS_TAB, row, column, **kwargs)
        self.addChildWidgets((
            ModelsNotebook.ModelsNotebook(self, 0, 0),
            ControlsFrame(self, 1, 0)
        ))

    def saveModelEvent(self, directory):
        file = open(os.path.join(directory, "settings.txt"), "w")
        self.sendEventToAll(lambda x: x.saveBciSettingsEvent(file))


class ControlsFrame(Frame.Frame, Savable.LoadableDirectory):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.MODELS_TAB_CONTROL_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self, c.MODELS_TAB_TRAIN_MODEL, 0, 0, command=self.trainButtonClicked),
            Buttons.Button(self, c.MODELS_TAB_LOAD_MODEL,  0, 1, command=self.loadEegClicked),
        ))

    def trainButtonClicked(self):
        self.sendEventToRoot(lambda x: x.trainButtonClickedEvent())

    def loadEegClicked(self):
        self.askLoadFile()

    def loadFromFile(self, directory):
        """
        askLoadFile calls this function when corresponding button is pressed.
        :param directory:
        :return:
        """
        self.sendEventToAll(lambda x: x.loadModelEvent(directory), True)
