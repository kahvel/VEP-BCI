__author__ = 'Anti'

from frames import PlusMinusFrame
from widgets import AbstractWidget
import Tkinter
import tkColorChooser


class Textbox(AbstractWidget.WidgetWithCommand):
    def __init__(self, name, row, column, **kwargs):
        AbstractWidget.WidgetWithCommand.__init__(self, name, row, column+1, **self.updateKwargs(kwargs, {
            "disabled_state": "readonly"
        }))
        self.width = kwargs.get("width", 5)
        self.arg_command = kwargs.get("command", None)

    def setValue(self, value):
        previous_state = self.widget.config("state")[4]
        self.widget.config(state=self.enabled_state)
        self.widget.delete(0, Tkinter.END)
        self.widget.insert(0, value)
        self.widget.config(state=previous_state)
        # Putting self.validate here makes UI very very slow, so we have to put validation after calling setValue

    def getValue(self):
        return self.widget.get()

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
            print(e)
            self.widget.configure(background="#ff0000")
            return False

    def validateOther(self):
        pass

    def createOtherWidget(self, parent):
        pass


class LabelTextbox(Textbox):
    def __init__(self, name, row, column, **kwargs):
        Textbox.__init__(self, name, row, column, **kwargs)
        self.allow_negative = kwargs.get("allow_negative", False)
        self.allow_zero = kwargs.get("allow_zero", False)

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
    def __init__(self, name, row, column, increase, decrease, **kwargs):
        LabelTextbox.__init__(self, name, row, column, **kwargs)
        self.increase_arg = increase
        self.decrease_arg = decrease

    def createOtherWidget(self, parent):
        LabelTextbox.createOtherWidget(self, parent)
        frame = PlusMinusFrame.PlusMinusFrame(self.row, self.column+1, self.increase, self.decrease)
        frame.create(parent)

    def increase(self):
        if self.validate():
            self.increase_arg()

    def decrease(self):
        if self.validate():
            self.decrease_arg()


class ColorTextbox(Textbox):
    def __init__(self, name, row, column, **kwargs):
        Textbox.__init__(self, name, row, column, **self.updateKwargs(kwargs, {
            "disabled_state": "readonly",
            "command": lambda color: self.button.configure(background=color),
            "default_value": "#eeeeee",
            "width": 7
        }))
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
        self.setValue(color)
        self.validate()