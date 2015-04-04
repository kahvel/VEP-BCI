__author__ = 'Anti'

from widgets import AbstractWidget
import Tkinter


class Checkbutton(AbstractWidget.WidgetWithCommand):
    def __init__(self, parent, name, row, column, **kwargs):
        AbstractWidget.WidgetWithCommand.__init__(self, name, row, column, **kwargs)
        self.command = kwargs.get("command", None)
        self.variable = Tkinter.IntVar()
        self.create(Tkinter.Checkbutton(parent, text=self.name, command=self.command, variable=self.variable))

    def getValue(self):
        return self.variable.get()

    def setValue(self, value):
        self.variable.set(value)
