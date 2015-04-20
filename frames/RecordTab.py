__author__ = 'Anti'

from widgets import Textboxes, Buttons
from frames import Frame
import constants as c


class RecordTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.RECORD_TAB, row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.LabelTextbox(self.widget, c.RECORD_LENGTH,    0, 3, command=int, default_value=1),
            Buttons.Button        (self.widget, c.RECORD_NEUTRAL,   0, 0),
            Buttons.Button        (self.widget, c.RECORD_TARGET,    0, 1),
            Buttons.Button        (self.widget, c.RECORD_THRESHOLD, 0, 2)
        ))