from gui_elements.widgets import Buttons
from gui_elements.widgets.frames import Frame
import ModelsNotebook
import constants as c
import Savable

import os


class ModelsTab(Frame.Frame, Savable.LoadableDirectory):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_NOTEBOOK_MODELS_TAB, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self, c.MODELS_TAB_LOAD_MODEL,  0, 1, command=self.loadEegClicked),
            ModelsNotebook.ModelsNotebook(self, 1, 0, columnspan=3)
        ))

    def loadEegClicked(self):
        self.askLoadFile()

    def loadFromFile(self, directory):
        """
        askLoadFile calls this function when corresponding button is pressed.
        :param directory:
        :return:
        """
        self.sendEventToAll(lambda x: x.loadModelEvent(directory), True)

    def saveModelEvent(self, directory):
        file = open(os.path.join(directory, "settings.txt"), "w")
        self.sendEventToAll(lambda x: x.saveBciSettingsEvent(file))
