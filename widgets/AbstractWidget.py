__author__ = 'Anti'

import Tkinter


class Widget(object):
    def __init__(self, name, row, column, columnspan=1, padx=5, pady=5):
        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.padx = padx
        self.pady = pady
        self.widget = None
        self.disabled = None
        self.name = name

    def loadDefaultValue(self):
        self.disabled = False

    def create(self, parent):
        self.widget = self.createWidget(parent)
        self.widget.grid(row=self.row, column=self.column, columnspan=self.columnspan, padx=self.padx, pady=self.pady)

    def createWidget(self, parent):
        raise NotImplementedError("createWidget not implemented!")

    def changeState(self, changer):
        raise NotImplementedError("changeState not implemented!")

    def enable(self, enabler):
        raise NotImplementedError("enable not implemented!")

    def disable(self, disabler):
        raise NotImplementedError("disable not implemented!")

    def save(self, file):
        raise NotImplementedError("save not implemented!")

    def load(self, file):
        raise NotImplementedError("load not implemented!")


class WidgetWithCommand(Widget):
    def __init__(self, name, command, disabled_state, row, column, columnspan=1, padx=5, pady=5, command_on_load=True, always_enabled=False):
        Widget.__init__(self, name, row, column, columnspan, padx, pady)
        self.command_on_load = command_on_load
        self.command = command

        self.disabled_state = disabled_state
        self.enabled_state = Tkinter.NORMAL

        self.disablers = []
        self.always_enabled = always_enabled

    def loadDefaultValue(self):
        Widget.loadDefaultValue(self)
        if self.command is not None and self.command_on_load:
            self.command()

    def changeState(self, changer):
        self.disabled = not self.disabled
        self.disable(changer) if self.disabled else self.enable(changer)

    def enable(self, enabler):
        if enabler in self.disablers:
            self.disablers.remove(enabler)
        if len(self.disablers) == 0:
            self.widget.config(state=self.enabled_state)

    def disable(self, disabler):
        if not self.always_enabled:
            self.disablers.append(disabler)
            self.widget.config(state=self.disabled_state)


class WidgetWithVariable(WidgetWithCommand):
    def __init__(self, name, command, disabled_state, variable, default_value, row, column, columnspan=1, padx=5, pady=5, command_on_load=True, always_enabled=False):
        WidgetWithCommand.__init__(self, name, command, disabled_state, row, column, columnspan, padx, pady, command_on_load, always_enabled)
        self.variable = variable
        self.default_value = default_value

    def loadDefaultValue(self):
        self.variable.set(self.default_value)
        WidgetWithCommand.loadDefaultValue(self)

    def save(self, file):
        file.write(str(self.variable.get())+"\n")

    def load(self, file):
        self.variable.set(file.readline())
