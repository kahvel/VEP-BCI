__author__ = 'Anti'

from frames import Frame
from widgets import Buttons


class PlusMinusFrame(Frame.Frame):
    def __init__(self, row, column, columnspan, padx, pady, increase, decrease):
        Frame.Frame.__init__(self, "PlusMinusTab", row, column, columnspan, padx, pady)
        self.addChildWidgets((
            Buttons.Button(" -", 0, 0, decrease, padx=0),
            Buttons.Button("+",  0, 1, increase, padx=0)
        ))