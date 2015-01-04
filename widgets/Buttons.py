__author__ = 'Anti'

from widgets import AbstractWidget
import Tkinter


class Button(AbstractWidget.WidgetWithCommand):
    def __init__(self, name, row, column, **kwargs):
        AbstractWidget.WidgetWithCommand.__init__(self, name, row, column, **kwargs)
        self.command = kwargs.get("command", None)

    def createWidget(self, parent):
        return Tkinter.Button(parent, text=self.name, command=self.command)

    def getValue(self):
        return

    def setValue(self, value):
        return


class SunkenButton(AbstractWidget.WidgetWithCommand):
    def __init__(self, name, row, column, **kwargs):
        AbstractWidget.WidgetWithCommand.__init__(self, name, row, column, **kwargs)
        self.command = kwargs.get("command", lambda: None)
        self.variable = Tkinter.IntVar()

    def getValue(self):
        return self.variable.get()

    def setValue(self, value):
        self.variable.set(value)

    def sunkenButtonCommand(self):
        self.variable.set(not self.variable.get())
        self.widget.config(relief=Tkinter.SUNKEN) if self.variable.get() else self.widget.config(relief=Tkinter.RAISED)
        if self.command is not None:
            self.command()

    def createWidget(self, parent):
        return Tkinter.Button(parent, text=self.name, command=self.sunkenButtonCommand)

