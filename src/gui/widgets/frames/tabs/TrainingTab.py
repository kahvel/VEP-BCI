from gui.widgets import Buttons, OptionMenu
from gui.widgets.frames import Frame
import constants as c
import Savable


class TrainingTab(Frame.Frame, Savable.Savable, Savable.Loadable):
    def __init__(self, parent, buttons, **kwargs):
        save, load = buttons
        self.main_window_save_eeg_function = save
        self.main_window_load_eeg_function = load
        Frame.Frame.__init__(self, parent, c.TRAINING_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenu(self.widget, c.TRAINING_RECORD,   0, 1, c.TRAINING_RECORD_NAMES),
            Buttons.Button       (self.widget, c.TRAINING_SAVE_EEG, 0, 3, command=self.askSaveFile),
            Buttons.Button       (self.widget, c.TRAINING_LOAD_EEG, 0, 4, command=self.askLoadFile),
            Buttons.Button       (self.widget, c.TRAINING_START,    1, 0)
        ))

    def saveToFile(self, file):
        self.main_window_save_eeg_function(file)

    def loadFromFile(self, file):
        self.main_window_load_eeg_function(file)
