__author__ = 'Anti'

import Tkinter

import copy

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
        self.reset_value = kwargs.get("reset_value", values[0])
        self.disabled_tabs = []

    def addOption(self, option, command=lambda x: None):
        self.widget["menu"].add_command(label=option, command=Tkinter._setit(self.variable, option, callback=command))

    def addDefaultOptions(self):
        for option in self.values:
            self.addOption(option)

    def addTargetOptions(self):
        for i, disabled in enumerate(self.disabled_tabs):
            if not disabled:
                self.addOption(i+1)

    def targetAdded(self):
        self.disabled_tabs.append(False)
        self.addOption(len(self.disabled_tabs))

    def deleteOptions(self):
        self.widget["menu"].delete(0, Tkinter.END)

    def updateAfterDeleteOrDisable(self, tab, additionalFunction=lambda x, y: None):
        tab += 1
        target = self.getValue()
        if target not in self.values:
            target = int(target)
            if target == tab:
                print("Warning: OptionMenu (" + self.name + ") in Test tab reset to " + self.reset_value)
                self.setValue(c.TEST_NONE)
            else:
                additionalFunction(target, tab)

    def decreaseLargerTabs(self, target, tab):
        if target > tab:
            self.setValue(target-1)

    def targetRemoved(self, deleted_tab):
        self.deleteOptions()
        self.addDefaultOptions()
        del self.disabled_tabs[deleted_tab]
        self.addTargetOptions()
        self.updateAfterDeleteOrDisable(deleted_tab, self.decreaseLargerTabs)

    def targetDisabled(self, tabs, current_tab):
        self.disabled_tabs = copy.deepcopy(tabs)
        self.deleteOptions()
        self.addDefaultOptions()
        self.addTargetOptions()
        self.updateAfterDeleteOrDisable(current_tab)

    def targetEnabled(self, tabs, current_tab):
        self.disabled_tabs = copy.deepcopy(tabs)
        self.deleteOptions()
        self.addDefaultOptions()
        self.addTargetOptions()
