__author__ = 'Anti'

import AbstractWidget
import Tkinter


class OptionMenu(AbstractWidget.WidgetWithVariable):
    def __init__(self, name, row, column, command=None, values=None, columnspan=2, padx=5, pady=5, default_value=None, command_on_load=True):
        AbstractWidget.WidgetWithVariable.__init__(self, name, command, "disabled", Tkinter.StringVar(), self.getDefaultValue(default_value, values), row, column, columnspan, padx, pady, command_on_load)
        self.values = values

    def getDefaultValue(self, value, values):
        return value if value is not None else values[0]

    def createWidget(self, parent):
        return Tkinter.OptionMenu(parent, self.variable, *self.values, command=lambda x: self.command())
