from gui.widgets import Buttons, OptionMenu
from gui.widgets.frames import Frame
import constants as c
import Savable


class RecordTab(Frame.Frame, Savable.Savable, Savable.Loadable):
    def __init__(self, parent, buttons, **kwargs):
        save, load, reset = buttons
        self.main_window_save_eeg_function = save
        self.main_window_load_eeg_function = load
        Frame.Frame.__init__(self, parent, c.RECORD_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenu(self, c.TRAINING_RECORD,    0, 1, c.TRAINING_RECORD_NAMES),
            Buttons.Button       (self, c.TRAINING_SAVE_EEG,  1, 0, command=self.askSaveFile),
            Buttons.Button       (self, c.TRAINING_LOAD_EEG,  1, 1, command=self.askLoadFile),
            Buttons.Button       (self, c.TRAINING_RESET_EEG, 1, 2, command=reset),
        ))

    def saveToFile(self, file):
        self.main_window_save_eeg_function(file)

    def loadFromFile(self, file):
        self.main_window_load_eeg_function(file)
