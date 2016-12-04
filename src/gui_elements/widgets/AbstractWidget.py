import Tkinter

from messaging.gui_messaging import MessagingInterface


class Widget(object):
    def __init__(self, parent, name, row, column, **kwargs):
        self.parent = parent
        self.row = row
        self.column = column
        self.columnspan = kwargs.get("columnspan", 1)
        self.no_value = kwargs.get("no_value", False)
        self.padx = kwargs.get("padx", 5)
        self.pady = kwargs.get("pady", 5)
        self.widget = None
        self.name = name
        self.disabled = None
        self.default_disability = kwargs.get("default_disability", False)
        self.default_disablers = kwargs.get("default_disablers", [])
        self.disablers = None
        self.always_enabled = kwargs.get("always_enabled", False)

    def setDefaultKwargs(self, kwargs, default_values):
        for key in default_values:
            kwargs.setdefault(key, default_values[key])
        return kwargs

    def loadDefaultValue(self):
        self.disabled = self.default_disability
        self.disablers = self.default_disablers

    def create(self, widget):
        self.widget = widget
        self.widget.grid(row=self.row, column=self.column, columnspan=self.columnspan, padx=self.padx, pady=self.pady)

    def createWidget(self, parent):
        raise NotImplementedError("createWidget not implemented!")

    def enable(self, enabler):
        if enabler in self.disablers:
            self.disablers.remove(enabler)
        if len(self.disablers) == 0:
            self.disabled = False

    def disable(self, disabler):
        if not self.always_enabled:
            if disabler not in self.disablers:
                self.disablers.append(disabler)
            self.disabled = True

    def saveBciSettingsEvent(self, file):
        file.write(self.name+";"+str(int(self.disabled))+";"+str(self.disablers).replace("'", "").strip("[]")+"\n")

    def loadBciSettingsEvent(self, file):
        name, disabled, disablers = file.readline().strip("\n").split(";")
        self.disabled = int(disabled)
        self.disablers = disablers.split(", ") if disablers != "" else []

    def getValue(self):
        raise NotImplementedError("getValue not implemented!")

    def setValue(self, value):
        raise NotImplementedError("setValue not implemented!")

    def getNotValidated(self):
        if not self.validate():
            return self.getValue()

    def validate(self):
        return True


class WidgetWithCommand(Widget, MessagingInterface.WidgetMessageHandler):
    def __init__(self, parent, name, row, column, **kwargs):
        Widget.__init__(self, parent, name, row, column, **kwargs)
        MessagingInterface.WidgetMessageHandler.__init__(self, parent)
        self.default_value = kwargs.get("default_value", 0)
        self.disabled_state = kwargs.get("disabled_state", "disabled")
        self.enabled_state = Tkinter.NORMAL

    def loadDefaultValue(self):
        self.setValue(self.default_value)
        Widget.loadDefaultValue(self)
        self.updateState()

    def loadBciSettingsEvent(self, file):
        name, value, disabled, disablers = file.readline().strip("\n").split(";")
        self.setValue(value)
        self.disabled = int(disabled)
        self.disablers = disablers.split(", ") if disablers != "" else []
        self.updateState()

    def updateState(self):
        self.widget.config(state=(self.disabled_state if self.disabled else self.enabled_state))

    def enable(self, enabler):
        Widget.enable(self, enabler)
        if len(self.disablers) == 0:
            self.widget.config(state=self.enabled_state)

    def disable(self, disabler):
        Widget.disable(self, disabler)
        if not self.always_enabled:
            self.widget.config(state=self.disabled_state)

    def saveBciSettingsEvent(self, file):
        file.write(self.name+";"+str(self.getValue())+";"+str(int(self.disabled))+";"+str(self.disablers).replace("'", "").strip("[]")+"\n")
