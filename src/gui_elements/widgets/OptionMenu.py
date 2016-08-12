from gui_elements.widgets.frames import Frame
from gui_elements.widgets import AbstractWidget

import Tkinter
import copy


class OptionMenu(AbstractWidget.WidgetWithCommand):
    def __init__(self, parent, name, row, column, values, **kwargs):
        AbstractWidget.WidgetWithCommand.__init__(self, parent, name, row, column, **self.setDefaultKwargs(kwargs, {
            "default_value": self.getDefaultValue(kwargs, values),
            "columnspan": kwargs.get("columnspan", 2)
        }))
        self.values = values
        self.variable = Tkinter.StringVar()
        self.command = kwargs.get("command", lambda x: None)
        label = Tkinter.Label(parent.widget, text=self.name)
        label.grid(row=self.row, column=self.column-1, padx=self.padx, pady=self.pady)
        self.create(Tkinter.OptionMenu(parent.widget, self.variable, *self.values, command=lambda x: self.command(x)))

    def getValue(self):
        return self.variable.get()

    def setValue(self, value):
        self.variable.set(value)

    def getDefaultValue(self, kwargs, values):
        return kwargs.get("default_value", values[0])


class OptionMenuFrame(Frame.Frame):
    def __init__(self, parent, name, row, column, values, **kwargs):
        Frame.Frame.__init__(self, parent, name, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu(self, name, 0, 1, values),
        ))


class EventOptionMenu(OptionMenu):
    def __init__(self, parent, name, row, column, values, **kwargs):
        OptionMenu.__init__(self, parent, name, row, column, values, **kwargs)
        self.reset_value = kwargs.get("reset_value", values[0])
        self.disabled_tabs = []

    def addOption(self, option):
        self.widget["menu"].add_command(label=option, command=Tkinter._setit(self.variable, option, callback=self.command))

    def addDefaultOptions(self):
        for option in self.values:
            self.addOption(option)

    def addOptions(self):
        for i, disabled in enumerate(self.disabled_tabs):
            if not disabled:
                self.addOption(i+1)

    def deleteOptions(self):
        self.widget["menu"].delete(0, Tkinter.END)

    def updateAfterDeleteOrDisable(self, tab, removed):
        tab += 1
        value = self.getValue()
        if value not in self.values:
            value = int(value)
            if value == tab:
                print("Warning: OptionMenu (" + self.name + ") reset to " + self.reset_value)
                self.setValue(self.reset_value)
            else:
                if removed:
                    self.decreaseLargerTabs(value, tab)

    def decreaseLargerTabs(self, target, tab):
        if target > tab:
            self.setValue(target-1)

    def deleteAndAddAll(self):
        self.deleteOptions()
        self.addDefaultOptions()
        self.addOptions()

    def saveBciSettingsEvent(self, file):
        file.write(self.name+";"+str(self.getValue())+";"+str(int(self.disabled))+";"+str(list(int(value) for value in self.disabled_tabs)).strip("[]")+";"+str(self.disablers).replace("'", "").strip("[]")+"\n")

    def loadBciSettingsEvent(self, file):
        name, value, disabled, disabled_tabs, disablers = file.readline().strip("\n").split(";")
        self.setValue(value)
        self.disabled = int(disabled)
        self.disablers = disablers.split(", ") if disablers != "" else []
        disabled_tabs_str = disabled_tabs.split(", ") if disabled_tabs != "" else []
        self.disabled_tabs = list(int(value) for value in disabled_tabs_str)
        self.deleteAndAddAll()

    def getValue(self):
        try:
            return int(self.variable.get())
        except:
            return self.variable.get()

    def eventAdded(self):
        self.disabled_tabs.append(False)
        self.addOption(len(self.disabled_tabs))

    def eventRemoved(self, deleted_tab):
        del self.disabled_tabs[deleted_tab]
        self.deleteAndAddAll()
        self.updateAfterDeleteOrDisable(deleted_tab, True)

    def eventDisabled(self, tabs, current_tab):
        self.disabled_tabs = copy.deepcopy(tabs)
        self.deleteAndAddAll()
        self.updateAfterDeleteOrDisable(current_tab, False)

    def eventEnabled(self, tabs):
        self.disabled_tabs = copy.deepcopy(tabs)
        self.deleteAndAddAll()


class ModelChoosingMenu(EventOptionMenu):
    def __init__(self, parent, name, row, column, values, **kwargs):
        EventOptionMenu.__init__(self, parent, name, row, column, values, **kwargs)

    def addNewModelTabEvent(self):
        self.eventAdded()

    def modelTabRemovedEvent(self, deleted_tab):
        self.eventRemoved(deleted_tab)

    def loadModelEvent(self, directory):
        self.eventAdded()

    def getChosenModelNumber(self):  # Currently not used
        self.sendEventToRoot(lambda x: x.sendChosenModelNumber(self.getValue()))


class RecordingChoosingMenu(EventOptionMenu):
    def __init__(self, parent, name, row, column, values, **kwargs):
        EventOptionMenu.__init__(self, parent, name, row, column, values, **kwargs)

    def addNewRecordingTabEvent(self):
        self.eventAdded()

    def recordTabRemovedEvent(self, deleted_tab):
        self.eventRemoved(deleted_tab)

    def loadEegEvent(self, directory):
        self.eventAdded()


class TargetChoosingMenu(EventOptionMenu):
    def __init__(self, parent, name, row, column, values, **kwargs):
        EventOptionMenu.__init__(self, parent, name, row, column, values, **kwargs)

    def targetAddedEvent(self):
        self.eventAdded()

    def targetRemovedEvent(self, deleted_tab):
        self.eventRemoved(deleted_tab)

    def targetDisabledEvent(self, tabs, current_tab):
        self.eventDisabled(tabs, current_tab)

    def targetEnabledEvent(self, tabs, current_tab):
        self.eventEnabled(tabs)
