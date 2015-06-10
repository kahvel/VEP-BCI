import Tkinter
import tkColorChooser

from gui.widgets.frames import PlusMinusFrame, Frame
from gui.widgets import AbstractWidget, Buttons
import constants as c


class Textbox(AbstractWidget.WidgetWithCommand):
    def __init__(self, parent, name, row, column, **kwargs):
        AbstractWidget.WidgetWithCommand.__init__(self, name, row, column, **self.setDefaultKwargs(kwargs, {
            "disabled_state": "readonly"
        }))
        self.width = kwargs.get("width", 5)
        self.arg_command = kwargs.get("command", lambda x: None)
        self.auto_update = kwargs.get("auto_update", lambda: True)
        self.validate_command = lambda: self.auto_update() if self.validate() else False
        self.create(Tkinter.Entry(parent, validate="focusout", validatecommand=self.validate_command, width=self.width))

    def setValue(self, value):
        previous_state = self.widget.config("state")[4]
        self.widget.config(state=self.enabled_state)
        self.widget.delete(0, Tkinter.END)
        self.widget.insert(0, value)
        self.widget.config(state=previous_state)
        self.validate()

    def loadDefaultValue(self):
        AbstractWidget.WidgetWithCommand.loadDefaultValue(self)
        self.auto_update()

    def getValue(self):
        return self.toInt(self.widget.get())

    def toFloat(self, value):  # Try to convert to float. If fails, return value itself.
        try:
            return float(value)
        except ValueError:
            return value

    def toInt(self, value):  # Try to convert to int. If fails, try to convert to float.
        try:
            return int(value)
        except ValueError:
            return self.toFloat(value)

    def validate(self):
        if not self.disabled:
            try:
                self.validationFunction()
                self.widget.configure(background="#ffffff")
                return True
            except Exception, e:
                print("validation", self.name, e)
                self.widget.configure(background="#ff0000")
                return False
        else:
            return True

    def validationFunction(self):
        ret = self.arg_command(self.widget.get())
        if isinstance(ret, bool):
            assert ret


class LabelTextbox(Textbox):
    def __init__(self, parent, name, row, column, **kwargs):
        label_columnspan = kwargs.get("label_columnspan", 1)
        Textbox.__init__(self, parent, name, row, column+label_columnspan, **kwargs)
        self.allow_negative = kwargs.get("allow_negative", False)
        self.allow_zero = kwargs.get("allow_zero", False)
        label = Tkinter.Label(parent, text=self.name)
        label.grid(row=self.row, column=column, padx=self.padx, pady=self.pady, columnspan=label_columnspan)

    def validationFunction(self):
        if not self.allow_negative:
            assert float(self.widget.get()) >= 0
        if not self.allow_zero:
            assert float(self.widget.get()) != 0
        Textbox.validationFunction(self)


class SequenceTextbox(LabelTextbox):
    def __init__(self, parent, name, row, column, **kwargs):
        LabelTextbox.__init__(self, parent, name, row, column, **kwargs)

    def loadDefaultValue(self):  # This is needed to get correct default values to frequency and this textbox
        self.disabled = self.default_disability
        self.disablers = self.default_disablers
        self.updateState()

    def getValue(self):  # This is needed to keep value as string
        return self.widget.get()


class PlusMinusTextboxFrame(Frame.Frame):
    def __init__(self, parent, name, row, column, increase, decrease, **kwargs):
        Frame.Frame.__init__(self, parent, name, row, column, **self.setDefaultKwargs(kwargs, {
            "columnspan": 3
        }))
        increase_command = lambda: increase() if self.widgets_dict[c.TEXTBOX].validate() else None
        decrease_command = lambda: decrease() if self.widgets_dict[c.TEXTBOX].validate() else None
        self.addChildWidgets((
            LabelTextbox(self.widget, c.TEXTBOX, 0, 0, command=float, auto_update=kwargs["command"], default_value=10.0),
            PlusMinusFrame.PlusMinusFrame(self.widget, 0, 2, increase_command, decrease_command)
        ))

    def getValue(self):
        return self.widgets_dict[c.TEXTBOX].getValue()


class ColorTextboxFrame(Frame.Frame):
    def __init__(self, parent, button_name, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, button_name, row, column, **self.setDefaultKwargs(kwargs, {
            "columnspan": 2
        }))
        button_command = lambda: self.chooseColor(self.widgets_dict[c.TEXTBOX])
        textbox_command = lambda color: self.widgets_dict[button_name].widget.configure(background=color)
        default_value = kwargs.get("default_value", "#eeeeee")
        self.addChildWidgets((
            Buttons.Button(self.widget, button_name, 0, 0, command=button_command),
            Textbox(self.widget, c.TEXTBOX, 0, 1, disabled_state="readonly", command=textbox_command, default_value=default_value, width=7)
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

    def getValue(self):
        return self.widgets_dict[c.TEXTBOX].getValue()


class HarmonicTextbox(LabelTextbox):
    def __init__(self, parent, name, row, column, **kwargs):
        LabelTextbox.__init__(self, parent, name, row, column, command=self.harmonicsValidation, **kwargs)

    def getValue(self):
        return list(map(float, self.widget.get().split(",")))

    def harmonicsValidation(self, value):
        for v in value.split(","):
            assert float(v) > 0

    def save(self, file):  # To save value as string, not as list
        file.write(self.name+";"+str(self.widget.get())+";"+str(int(self.disabled))+";"+str(self.disablers).replace("'", "").strip("[]")+"\n")
