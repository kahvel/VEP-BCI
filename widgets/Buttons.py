__author__ = 'Anti'

import AbstractWidget
import Tkinter


class Button(AbstractWidget.WidgetWithCommand):
    def __init__(self, name, row, column, command=None, columnspan=1, padx=5, pady=5, command_on_load=True, always_enabled=False):
        AbstractWidget.WidgetWithCommand.__init__(self, name, command, "disabled", row, column, columnspan, padx, pady, command_on_load, always_enabled)

    def createWidget(self, parent):
        return Tkinter.Button(parent, text=self.name, command=self.command)


class SunkenButton(AbstractWidget.WidgetWithVariable):
    def __init__(self, name, row, column, command=None, columnspan=1, padx=5, pady=5, default_value=0, command_on_load=True, always_enabled=False):
        AbstractWidget.WidgetWithVariable.__init__(self, name, self.sunkenButtonCommand, "disabled", Tkinter.BooleanVar(), default_value, row, column, columnspan, padx, pady, command_on_load, always_enabled)
        self.sunken_button_command = command

    def sunkenButtonCommand(self):
        self.variable.set(not self.variable.get())
        self.widget.config(relief=Tkinter.RAISED) if self.variable.get() else self.widget.config(relief=Tkinter.SUNKEN)
        if self.sunken_button_command is not None:
            self.sunken_button_command()

    def createWidget(self, parent):
        return Tkinter.Button(parent, text=self.name, command=self.command)
