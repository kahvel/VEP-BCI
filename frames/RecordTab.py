__author__ = 'Anti'

from widgets import Textboxes, Buttons
from frames import Frame


class RecordTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, "Record", row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.LabelTextbox(self.widget, "Length",  0, 3, command=int, default_value=1),
            Buttons.Button(self.widget, "Neutral",         0, 0),
            Buttons.Button(self.widget, "Target",          0, 1),
            Buttons.Button(self.widget, "Threshold",       0, 2)
        ))