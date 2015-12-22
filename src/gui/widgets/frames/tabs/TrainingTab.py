from gui.widgets import Buttons
from gui.widgets.frames import Frame
import constants as c


class TrainingTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.TRAINING_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton(self.widget, c.TRAINING_RECORD,   0, 0),
            Buttons.Button      (self.widget, c.TRAINING_SAVE_EEG, 0, 1),
            Buttons.Button      (self.widget, c.TRAINING_START,    1, 0)
        ))
