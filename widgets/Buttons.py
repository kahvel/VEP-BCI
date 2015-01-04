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
        self.variable = Tkinter.IntVar()

    def getValue(self):
        return self.variable.get()

    def setValue(self, value):
        self.variable.set(value)

    def updateState(self):
        AbstractWidget.WidgetWithCommand.updateState(self)
        self.updateRelief()

    def updateRelief(self):
        self.widget.config(relief=Tkinter.SUNKEN) if self.variable.get() else self.widget.config(relief=Tkinter.RAISED)

    def sunkenButtonCommand(self):
        self.variable.set(not self.variable.get())
        self.updateRelief()

    def createWidget(self, parent):
        return Tkinter.Button(parent, text=self.name, command=self.sunkenButtonCommand)


class DisableButton(SunkenButton):
    def __init__(self, name, row, column, **kwargs):
        SunkenButton.__init__(self, name, row, column, **kwargs)
        self.enable_command = kwargs.get("enable", lambda: None)
        self.disable_command = kwargs.get("disable", lambda: None)

    def sunkenButtonCommand(self):
        SunkenButton.sunkenButtonCommand(self)
        if self.variable.get():
            self.disable_command(self.name)
        else:
            self.enable_command(self.name)

