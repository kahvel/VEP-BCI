__author__ = 'Anti'

from frames import Frame
from widgets import Radiobutton
import constants as c
import Tkinter


class RadiobuttonFrame(Frame.Frame):
    def __init__(self, parent, name, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, name, row, column, **kwargs)
        self.variable = Tkinter.StringVar(value=c.LINEAR_DETREND)
        self.default_value = kwargs.get("default_value", c.LINEAR_DETREND)
        self.addChildWidgets((
            Radiobutton.Radiobutton(self.widget, c.CONSTANT_DETREND, 0, 0, self.variable, padx=0, pady=0),
            Radiobutton.Radiobutton(self.widget, c.LINEAR_DETREND,   1, 0, self.variable, padx=0, pady=0)
        ))

    def getValue(self):
        return self.variable.get()

    def setValue(self, value):
        self.variable.set(value)

    def loadDefaultValue(self):
        self.setValue(self.default_value)

    # TODO add load and save