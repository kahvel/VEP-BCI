__author__ = 'Anti'

import Tkinter

from gui.widgets import AbstractWidget
import constants as c


class OptionMenu(AbstractWidget.WidgetWithCommand):
    def __init__(self, parent, name, row, column, values, **kwargs):
        AbstractWidget.WidgetWithCommand.__init__(self, name, row, column, **self.setDefaultKwargs(kwargs, {
            "default_value": self.getDefaultValue(kwargs, values),
            "columnspan": kwargs.get("columnspan", 2)
        }))
        self.values = values
        self.variable = Tkinter.StringVar()
        self.command = kwargs.get("command", lambda: None)
        label = Tkinter.Label(parent, text=self.name)
        label.grid(row=self.row, column=self.column-1, padx=self.padx, pady=self.pady)
        self.create(Tkinter.OptionMenu(parent, self.variable, *self.values, command=lambda x: self.command()))

    def getValue(self):
        return self.variable.get()

    def setValue(self, value):
        self.variable.set(value)

    def getDefaultValue(self, kwargs, values):
        return kwargs.get("default_value", values[0])


class TargetChoosingMenu(OptionMenu):
    def __init__(self, parent, name, row, column, values, **kwargs):
        OptionMenu.__init__(self, parent, name, row, column, values, **kwargs)
        self.target_count = 0
        self.reset_value = kwargs.get("reset_value", values[0])

    def addOption(self, option, command=lambda x: None):
        self.widget["menu"].add_command(label=option, command=Tkinter._setit(self.variable, option, callback=command))

    def addDefaultOptions(self):
        for option in self.values:
            self.addOption(option)

    def addTargetOptions(self):
        for i in range(1, self.target_count+1):
            self.addOption(i)

    def targetAdded(self):
        self.target_count += 1
        self.addOption(self.target_count)

    def deleteOptions(self):
        self.widget["menu"].delete(0, Tkinter.END)

    def updateOptionMenu(self, deleted_tab):
        deleted_tab += 1
        target = self.getValue()
        if target not in self.values:
            target = int(target)
            if target == deleted_tab:
                print("Warning: OptionMenu (" + self.name + ") in Test tab reset to " + self.reset_value)
                self.setValue(c.TEST_NONE)
            elif target > deleted_tab:
                self.setValue(target-1)

    def targetRemoved(self, deleted_tab):
        self.deleteOptions()
        self.addDefaultOptions()
        self.target_count -= 1
        self.addTargetOptions()
        self.updateOptionMenu(deleted_tab)
