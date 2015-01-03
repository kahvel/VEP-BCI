__author__ = 'Anti'

import AbstractFrame
from widgets import AbstractWidget
import math


class TargetsTab(AbstractFrame.Tab):
    def __init__(self, parent):
        AbstractFrame.Tab.__init__(self, parent)
        freq_textbox = AbstractWidget.LabelTextbox("Freq", 0, 0, float, False, False)
        self.frame_widgets = ((
            freq_textbox,
            (
                AbstractWidget.Button(" -", 0, 0, )
            )

        ),)
        self.createFrame()

    def validateFreq(self, textbox, d=0):
        return textbox, lambda x: self.changeFreq(x, d)

    def changeFreq(self, textbox, variable, d):
        target_freq = float(textbox.widget.get())
        monitor_freq = int(self.frequency_textbox.get())
        freq_on = math.floor(monitor_freq/target_freq/2)
        freq_off = math.ceil(monitor_freq/target_freq/2)
        textbox.updateValue(float(monitor_freq)/(freq_off+freq_on+d))

    def frameGenerator(self, parent):
        textboxes["Freq"] = MyWindows.newTextBox(frame, "Freq", self.validate_commands["Freq"]["Normal"])
        MyWindows.newButtonFrame(frame, [" -", "+"], [lambda: self.validate_commands["Freq"]["Decrease"](textboxes["Freq"]), lambda: self.validate_commands["Freq"]["Increase"](textboxes["Freq"])], buttons=buttons, padx=0).grid(row=0, column=2)
        textboxes["Delay"] = MyWindows.newTextBox(frame, "Delay", self.validate_commands["Delay"], column=4)
        textboxes["Width"] = MyWindows.newTextBox(frame, "Width", self.validate_commands["Width"], row=1)
        textboxes["Height"] = MyWindows.newTextBox(frame, "Height", self.validate_commands["Height"], column=2, row=1)
        textboxes["Color1"], buttons["Color1"] = MyWindows.newColorButton(frame, "Color1", self.validate_commands["Color1"], column=4, row=1)
        textboxes["x"] = MyWindows.newTextBox(frame, "x", self.validate_commands["x"], row=2)
        textboxes["y"] = MyWindows.newTextBox(frame, "y", self.validate_commands["y"], column=2, row=2)
        textboxes["Color2"], buttons["Color2"] = MyWindows.newColorButton(frame, "Color2", self.validate_commands["Color2"], column=4, row=2)
        return frame
 a=   {
            "Height": lambda textbox: MyWindows.validateInt(textbox, False, False),
            "Width": lambda textbox: MyWindows.validateInt(textbox, False, False),
            "Color1": lambda textbox, button: MyWindows.validateColor(textbox, button),
            "Color2": lambda textbox, button: MyWindows.validateColor(textbox, button),
            "x": lambda textbox: MyWindows.validateInt(textbox, True, True),
            "y": lambda textbox: MyWindows.validateInt(textbox, True, True),
            "Freq": {
                "Normal": lambda textbox: self.validateFreq(textbox, False, False, 0),
                "Increase": lambda textbox: self.validateFreq(textbox, False, False, -1),
                "Decrease": lambda textbox: self.validateFreq(textbox, False, False, 1),
            },
            "Delay": lambda textbox: MyWindows.validateInt(textbox, False, True)
    }