__author__ = 'Anti'

from widgets import AbstractWidget
import Tkinter


class Checkbutton(AbstractWidget.WidgetWithVariable):
    def __init__(self, name, row, column, command=None, columnspan=1, padx=5, pady=5, default_value=0, command_on_load=True):
        AbstractWidget.WidgetWithVariable.__init__(self, name, command, "disabled", Tkinter.BooleanVar(), default_value, row, column, columnspan, padx, pady, command_on_load)

    def createWidget(self, parent):
        return Tkinter.Checkbutton(parent, text=self.name, command=self.command, variable=self.variable)