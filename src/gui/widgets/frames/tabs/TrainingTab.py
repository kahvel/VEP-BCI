from gui.widgets import Buttons
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
            Buttons.SunkenButton(self.widget, c.TRAINING_RECORD_NORMAL,   0, 0),
            Buttons.Button      (self.widget, c.TRAINING_SAVE_EEG, 0, 1, command=self.askSaveFile),
            Buttons.Button      (self.widget, c.TRAINING_LOAD_EEG, 0, 2, command=self.askLoadFile),
            Buttons.Button      (self.widget, c.TRAINING_START,    1, 0)
        ))

    def save(self, file):
        self.main_window_save_eeg_function(file)

    def load(self, file):
        self.main_window_load_eeg_function(file)
