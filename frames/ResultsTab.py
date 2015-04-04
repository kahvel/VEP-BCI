__author__ = 'Anti'

from widgets import Buttons
from frames import Frame


class ResultsTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, "Results", row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self.widget, "Show",  0, 0),
            Buttons.Button(self.widget, "Reset", 0, 1)
        ))