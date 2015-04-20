__author__ = 'Anti'

from frames import Frame
from widgets import Buttons
import constants as c


class PlusMinusFrame(Frame.Frame):
    def __init__(self, parent, row, column, increase, decrease, **kwargs):
        Frame.Frame.__init__(self, parent, c.PLUS_MINUS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self.widget, c.MINUS, 0, 0, command=decrease, padx=0),
            Buttons.Button(self.widget, c.PLUS,  0, 1, command=increase, padx=0)
        ))