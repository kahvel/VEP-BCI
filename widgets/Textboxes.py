__author__ = 'Anti'

from frames import PlusMinusFrame
from widgets import AbstractWidget
import Tkinter
import tkColorChooser


class Textbox(AbstractWidget.WidgetWithCommand):
    def __init__(self, name, row, column, command=None, columnspan=1, padx=5, pady=5, width=5, default_value=0, command_on_load=True):
        AbstractWidget.WidgetWithCommand.__init__(self, name, self.validate, "readonly", row, column+1, columnspan, padx, pady, command_on_load)
        self.default_value = default_value
        self.width = width
        self.arg_command = command

    def loadDefaultValue(self):
        self.updateValue(self.default_value)
        self.validate()
        AbstractWidget.Widget.loadDefaultValue(self)

    def updateValue(self, value):
        previous_state = self.widget.config("state")[4]
        self.widget.config(state=self.enabled_state)
        self.widget.delete(0, Tkinter.END)
        self.widget.insert(0, value)
        self.widget.config(state=previous_state)
        # Putting self.validate here makes UI very very slow, so we have to put validation after calling updateValue

    def createWidget(self, parent):
        main_widget = Tkinter.Entry(parent, validate="focusout", validatecommand=self.validate, width=self.width)
        self.createOtherWidget(parent)
        return main_widget

    def validate(self):
        try:
            self.validateOther()
            self.widget.configure(background="#ffffff")
            return True
        except Exception, e:
            self.widget.configure(background="#ff0000")
            return False

    def validateOther(self):
        pass

    def createOtherWidget(self, parent):
        pass

    def save(self, file):
        file.write(self.widget.get()+"\n")

    def load(self, file):
        self.updateValue(file.readline().strip())
        self.validate()


class LabelTextbox(Textbox):
    def __init__(self, name, row, column, command=None, allow_negative=False, allow_zero=False, columnspan=1, padx=5, pady=5, width=5, default_value=0, command_on_load=True):
        Textbox.__init__(self, name, row, column, command, columnspan, padx, pady, width, default_value, command_on_load)
        self.allow_negative = allow_negative
        self.allow_zero = allow_zero

    def validateOther(self):
        if not self.allow_negative:
            assert float(self.widget.get()) >= 0
        if not self.allow_zero:
            assert float(self.widget.get()) != 0
        self.arg_command(self.widget.get())

    def createOtherWidget(self, parent):
        label = Tkinter.Label(parent, text=self.name)
        label.grid(row=self.row, column=self.column-1, columnspan=self.columnspan, padx=self.padx, pady=self.pady)


class PlusMinusTextbox(LabelTextbox):
    def __init__(self, name, row, column, increase, decrease, command=None, allow_negative=False, allow_zero=False, columnspan=1, padx=5, pady=5, width=5, default_value=0, command_on_load=True):
        LabelTextbox.__init__(self, name, row, column, command, allow_negative, allow_zero, columnspan, padx, pady, width, default_value, command_on_load)
        self.increase_arg = increase
        self.decrease_arg = decrease

    def createOtherWidget(self, parent):
        LabelTextbox.createOtherWidget(self, parent)
        frame = PlusMinusFrame(self.row, self.column+1, self.columnspan, self.padx, self.pady, self.increase, self.decrease)
        frame.create(parent)

    def increase(self):
        if self.validate():
            self.increase_arg()

    def decrease(self):
        if self.validate():
            self.decrease_arg()


class ColorTextbox(Textbox):
    def __init__(self, name, row, column, command=None, columnspan=1, padx=5, pady=5, width=7, default_value="#eeeeee", command_on_load=True):
        Textbox.__init__(self, name, row, column, lambda color: self.button.configure(background=color), columnspan, padx, pady, width, default_value, command_on_load)
        self.button = None

    def createOtherWidget(self, parent):
        self.button = Tkinter.Button(parent, text=self.name, command=self.chooseColor)
        self.button.grid(row=self.row, column=self.column-1, columnspan=self.columnspan, padx=self.padx, pady=self.pady)

    def validateOther(self):
        self.arg_command(self.widget.get())

    def chooseColor(self):
        previous = self.widget.get()
        try:
            color = tkColorChooser.askcolor(previous)[1]
        except:
            color = tkColorChooser.askcolor()[1]
        if color is None:
            color = previous
        self.updateValue(color)
        self.validate()