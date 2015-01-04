__author__ = 'Anti'

from frames import PlusMinusFrame, Frame
from widgets import AbstractWidget, Buttons
import Tkinter
import tkColorChooser


class Textbox(AbstractWidget.WidgetWithCommand):
    def __init__(self, name, row, column, **kwargs):
        AbstractWidget.WidgetWithCommand.__init__(self, name, row, column+1, **self.updateKwargs(kwargs, {
            "disabled_state": "readonly"
        }))
        self.width = kwargs.get("width", 5)
        self.arg_command = kwargs.get("command", lambda x: None)
        self.auto_update = kwargs.get("auto_update", lambda: True)

    def setValue(self, value):
        previous_state = self.widget.config("state")[4]
        self.widget.config(state=self.enabled_state)
        self.widget.delete(0, Tkinter.END)
        self.widget.insert(0, value)
        self.widget.config(state=previous_state)
        self.validate()

    def getValue(self):
        return self.widget.get()

    def createWidget(self, parent):
        main_widget = Tkinter.Entry(parent, validate="focusout", validatecommand=lambda: self.auto_update() if self.validate() else False, width=self.width)
        self.createOtherWidget(parent)
        return main_widget

    def validate(self):
        print("asd")
        try:
            self.validateOther()
            self.widget.configure(background="#ffffff")
            return True
        except Exception, e:
            print("validation", e)
            self.widget.configure(background="#ff0000")
            return False

    def validateOther(self):
        self.arg_command(self.widget.get())

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


class PlusMinusTextboxFrame(Frame.Frame):
    def __init__(self, name, row, column, increase, decrease, **kwargs):
        Frame.Frame.__init__(self, "PlusMinusTextboxFrame", row, column, **self.updateKwargs(kwargs, {
            "columnspan": 3
        }))
        increase_command = lambda: increase() if self.widgets_dict[name].validate() else None
        decrease_command = lambda: decrease() if self.widgets_dict[name].validate() else None
        self.addChildWidgets((
            LabelTextbox(name, 0, 0, command=float, auto_update=kwargs["command"], default_value=10.0),
            PlusMinusFrame.PlusMinusFrame(0, 2, increase_command, decrease_command)
        ))


class ColorTextboxFrame(Frame.Frame):
    def __init__(self, name, row, column, **kwargs):
        Frame.Frame.__init__(self, "ColorTextboxFrame", row, column, **self.updateKwargs(kwargs, {
            "columnspan": 2
        }))
        button_command = lambda: self.chooseColor(self.widgets_dict["Textbox"])
        textbox_command = lambda color: self.widgets_dict[name].widget.configure(background=color)
        default_value = kwargs.get("default_value", "#eeeeee")
        self.addChildWidgets((
            Buttons.Button(name, 0, 0, command=button_command),
            Textbox("Textbox", 0, 1, disabled_state="readonly", command=textbox_command, default_value=default_value, width=7)
        ))

    def chooseColor(self, textbox):
        previous = textbox.getValue()
        try:
            color = tkColorChooser.askcolor(previous)[1]
        except:
            color = tkColorChooser.askcolor()[1]
        if color is None:
            color = previous
        textbox.setValue(color)
