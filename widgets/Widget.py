__author__ = 'Anti'

import Tkinter


class Widget(object):
    def __init__(self, create_widget, name, command, disabled_state, row, column, columnspan=1, padx=5, pady=5):
        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.padx = padx
        self.pady = pady

        self.widget = None
        self.create_widget = create_widget
        self.name = name
        self.command = command

        self.disabled_state = disabled_state
        self.enabled_state = Tkinter.NORMAL
        self.disabled = None

    def createWidget(self, parent):
        return self.create_widget(parent, text=self.name, command=self.command)

    def create(self, parent):
        self.widget = self.createWidget(parent)
        self.widget.grid(row=self.row, column=self.column, columnspan=self.columnspan, padx=self.padx, pady=self.pady)

    def loadDefaultValue(self):
        self.disabled = False

    def changeState(self):
        self.disabled = not self.disabled
        self.disable() if self.disabled else self.enable()

    def enable(self):
        self.widget.config(state=self.enabled_state)

    def disable(self):
        self.widget.config(state=self.disabled_state)


class WidgetWithVariable(Widget):
    def __init__(self, create_widget, name, command, disabled_state, variable, default_value, row, column, columnspan=1, padx=5, pady=5):
        Widget.__init__(self, create_widget, name, self.variablesCommand, disabled_state, row, column, columnspan, padx, pady)
        self.variable = variable
        self.default_value = default_value
        self.variables_command = command

    def loadDefaultValue(self):
        Widget.loadDefaultValue(self)
        self.variable.set(self.default_value)
        if self.command is not None:
            self.command()

    def variablesCommand(self):
        if self.variables_command is not None:
            self.variables_command(self.variable)


class WidgetWithTkinterVariable(WidgetWithVariable):
    def __init__(self, create_widget, name, command, disabled_state, variable, default_value, row, column, columnspan=1, padx=5, pady=5):
        WidgetWithVariable.__init__(self, create_widget, name, command, disabled_state, variable, default_value, row, column, columnspan, padx, pady)

    def createWidget(self, parent):
        return self.create_widget(parent, text=self.name, command=self.command, variable=self.variable)


class WidgetWithoutTkinterVariable(WidgetWithVariable):
    def __init__(self, create_widget, name, command, disabled_state, variable, default_value, row, column, columnspan=1, padx=5, pady=5):
        WidgetWithVariable.__init__(self, create_widget, name, self.variableChangeCommand, disabled_state, variable, default_value, row, column, columnspan, padx, pady)
        self.without_variable_command = command

    def variableChangeCommand(self, variable):
        variable.set(not variable.get())
        self.without_variable_command()


class Textbox(Widget):
    def __init__(self, name, command, allow_negative, allow_zero, default_value, row, column, columnspan=1, padx=5, pady=5, width=5):
        Widget.__init__(self, Tkinter.Entry, name, command, "readonly", row, column+1, columnspan, padx, pady)
        self.default_value = default_value
        self.width = width
        self.allow_negative = allow_negative
        self.allow_zero = allow_zero

    def loadDefaultValue(self):
        Widget.loadDefaultValue(self)
        previous_state = self.widget.config("state")[4]
        self.widget.config(state=self.enabled_state)
        self.widget.delete(0, Tkinter.END)
        self.widget.insert(0, self.default_value)
        self.widget.config(state=previous_state)

    def createWidget(self, parent):
        label = Tkinter.Label(parent, text=self.name)
        label.grid(row=self.row, column=self.column-1, columnspan=self.columnspan, padx=self.padx, pady=self.pady)
        return Tkinter.Entry(parent, validate="focusout", validatecommand=self.validate, width=self.width)

    def validate(self):
        try:
            if not self.allow_negative:
                assert float(self.widget.get()) >= 0
            if not self.allow_zero:
                assert float(self.widget.get()) != 0
            self.command(self.widget.get())
            self.widget.configure(background="#ffffff")
            return True
        except:
            self.widget.configure(background="#ff0000")
            return False


class OptionMenu(WidgetWithTkinterVariable):
    def __init__(self, name, command, variable, values, default_value, row, column, columnspan=2, padx=5, pady=5):
        WidgetWithTkinterVariable.__init__(self, Tkinter.OptionMenu, name, command, "disabled", variable, default_value, row, column, columnspan, padx, pady)
        self.values = values

    def createWidget(self, parent):
        return Tkinter.OptionMenu(parent, self.variable, *self.values, command=self.command)


class SunkenButton(WidgetWithoutTkinterVariable):
    def __init__(self, name, command, row, column, columnspan=1, padx=5, pady=5):
        WidgetWithoutTkinterVariable.__init__(self, Tkinter.Button, name, self.sunkenButtonCommand, "disabled", Tkinter.BooleanVar(), 0, row, column, columnspan, padx, pady)
        self.sunken_button_command = command

    def sunkenButtonCommand(self):
        self.widget.config(relief=Tkinter.RAISED) if self.variable.get() else self.widget.config(relief=Tkinter.SUNKEN)
        self.sunken_button_command(self.variable)
