from gui.widgets import Buttons, Textboxes
from gui.widgets.frames import Frame
import constants as c


class TrainingTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.TRAINING_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            Buttons.Button        (self.widget, c.TRAINING_RECORD, 0, 0),
            Textboxes.LabelTextbox(self.widget, c.TRAINING_LENGTH, 0, 2, command=int, default_value=1),
            Buttons.Button        (self.widget, c.TRAINING_START,  1, 0)
        ))
