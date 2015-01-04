__author__ = 'Anti'

from widgets import Textboxes, Buttons
from frames import Frame


class RecordTab(Frame.Frame):
    def __init__(self, row, column, **kwargs):
        Frame.Frame.__init__(self, "Record", row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.LabelTextbox("Length",  0, 3, command=int, default_value=1),
            Buttons.Button("Neutral",         0, 0),
            Buttons.Button("Target",          0, 1),
            Buttons.Button("Threshold",       0, 2)
        ))