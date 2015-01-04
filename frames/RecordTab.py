__author__ = 'Anti'

from widgets import Frame, Textboxes, Buttons


class RecordTab(Frame.Frame):
    def __init__(self, row, column, columnspan, padx, pady):
        Frame.Frame.__init__(self, "Record", row, column, columnspan, padx, pady)
        self.addChildWidgets((
            Textboxes.LabelTextbox("Length",  0, 3, int, False, False, default_value=1),
            Buttons.Button("Neutral",         0, 0),
            Buttons.Button("Target",          0, 1),
            Buttons.Button("Threshold",       0, 2)
        ))