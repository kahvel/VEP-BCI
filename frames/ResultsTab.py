__author__ = 'Anti'

from widgets import Buttons
from frames import Frame
import constants as c


class ResultsTab(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.RESULTS_TAB, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self.widget, c.RESULT_SHOW,  0, 0),
            Buttons.Button(self.widget, c.RESULT_RESET, 0, 1)
        ))