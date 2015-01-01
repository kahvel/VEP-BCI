__author__ = 'Anti'

import math
import Tkinter
import Notebook
from main_window import MyWindows


class TargetNotebook(Notebook.Notebook):
    def __init__(self, parent):
        Notebook.Notebook.__init__(self, parent)
        self.frequency_textbox = None
        self.default_tab_count = 6
        self.color_button_keys = ["Color1", "Color2"]
        self.addInitialTabs()
        self.default_values = {"Height": 150,
                               "Width": 150,
                               "x": 0,
                               "y": 0,
                               "Freq": 10.0,
                               "Color1": "#ffffff",
                               "Color2": "#777777",
                               "Delay": 0}

    def loadDefaultValues(self):
        for key in self.default_values:
            MyWindows.updateTextbox(self.textboxes[-1][key], self.default_values[key])
        for key in self.buttons[-1]:
            if key in self.color_button_keys:
                MyWindows.validateColor(self.buttons[-1][key], self.textboxes[-1][key])

    def frameGenerator(self, parent):
        frame = Tkinter.Frame(parent)
        textboxes, disable_var, buttons = self.textboxes[-1], self.disable_vars[-1], self.buttons[-1]
        textboxes["Freq"] = MyWindows.newTextBox(frame, "Freq", validatecommand=self.validateFreq)
        MyWindows.newButtonFrame(frame, [" -", "+"], [lambda: self.validateFreq(textboxes["Freq"], 1), lambda: self.validateFreq(textboxes["Freq"], -1)], buttons=buttons, padx=0).grid(row=0, column=2)
        textboxes["Delay"] = MyWindows.newTextBox(frame, "Delay", 4)
        textboxes["Width"] = MyWindows.newTextBox(frame, "Width", row=1)
        textboxes["Height"] = MyWindows.newTextBox(frame, "Height", 2, 1)
        textboxes["Color1"], buttons["Color1"] = MyWindows.newColorButton(frame, "Color1", 4, 1)
        textboxes["x"] = MyWindows.newTextBox(frame, "x", row=2)
        textboxes["y"] = MyWindows.newTextBox(frame, "y", 2, 2)
        textboxes["Color2"], buttons["Color2"] = MyWindows.newColorButton(frame, "Color2", 4, 2)
        return frame

    def setFrequencyTextbox(self, frequency_textbox):
        self.frequency_textbox = frequency_textbox

    def changeFreq(self, textbox, d):
        target_freq = float(textbox.get())
        monitor_freq = int(self.frequency_textbox.get())
        freq_on = math.floor(monitor_freq/target_freq/2)
        freq_off = math.ceil(monitor_freq/target_freq/2)
        MyWindows.updateTextbox(textbox, float(monitor_freq)/(freq_off+freq_on+d))

    def changeAllFreqs(self):
        for textbox in self.textboxes:
            self.validateFreq(textbox["Freq"])

    def validateFreq(self, textbox, d=0):
        return MyWindows.validate(textbox, lambda x: self.changeFreq(x, d))

    def loadValues(self, values):
        Notebook.Notebook.loadValues(self, values)
        for key in self.buttons[-1]:
            if key in self.color_button_keys:
                MyWindows.validateColor(self.buttons[-1][key], self.textboxes[-1][key])

    def defaultDisability(self):
        for i in range(2, self.tab_count+1):
            MyWindows.updateVar(self.disable_vars[i], 1)
        self.disableTabs()