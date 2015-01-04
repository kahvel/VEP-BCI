__author__ = 'Anti'

from widgets import Buttons
from frames import Frame


class ResultsTab(Frame.Frame):
    def __init__(self, row, column, columnspan, padx, pady):
        Frame.Frame.__init__(self, "Results", row, column, columnspan, padx, pady)
        self.addChildWidgets((
            Buttons.Button("Show",  0, 0),
            Buttons.Button("Reset", 0, 1)
        ))