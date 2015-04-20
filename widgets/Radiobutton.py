__author__ = 'Anti'

from widgets import AbstractWidget
import Tkinter


class Radiobutton(AbstractWidget.WidgetWithCommand):
    def __init__(self, parent, name, row, column, variable, **kwargs):
        AbstractWidget.WidgetWithCommand.__init__(self, name, row, column, **kwargs)
        self.command = kwargs.get("command", None)
        self.create(Tkinter.Radiobutton(parent, text=self.name, command=self.command, variable=variable, value=self.name))
