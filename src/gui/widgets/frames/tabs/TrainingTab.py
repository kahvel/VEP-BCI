from gui.widgets import Buttons
from gui.widgets.frames import Frame
import constants as c
import Savable


class TrainingTab(Frame.Frame, Savable.Savable):
    def __init__(self, parent, buttons, **kwargs):
        save, = buttons
        self.main_window_save_eeg_function = save
        Frame.Frame.__init__(self, parent, c.TRAINING_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton(self.widget, c.TRAINING_RECORD,   0, 0),
            Buttons.Button      (self.widget, c.TRAINING_SAVE_EEG, 0, 1, command=self.askSaveFile),
            Buttons.Button      (self.widget, c.TRAINING_START,    1, 0)
        ))

    def save(self, file):
        self.main_window_save_eeg_function(file)
