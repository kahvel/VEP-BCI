__author__ = 'Anti'

from frames import Frame
from widgets import Buttons


class PlusMinusFrame(Frame.Frame):
    def __init__(self, row, column, increase, decrease, **kwargs):
        Frame.Frame.__init__(self, "PlusMinusFrame", row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(" -", 0, 0, command=decrease, padx=0),
            Buttons.Button("+",  0, 1, command=increase, padx=0)
        ))