__author__ = 'Anti'

import math
import Tkinter
import Notebook
from main_window import MyWindows


class TargetNotebook(Notebook.Notebook):
    def __init__(self, parent, frequency_textbox):
        Notebook.Notebook.__init__(self, parent)
        self.frequency_textbox = frequency_textbox
        self.addInitialTabs()
        self.default_values = {"Height": 150,
                               "Width": 150,
                               "x": 0,
                               "y": 0,
                               "Freq": 10.0,
                               "Color1": "#ffffff",
                               "Color2": "#777777",
                               "Delay": 0}
        self.loadDefaultValues()

    def loadDefaultValues(self):
        for key in self.default_values:
            MyWindows.updateTextbox(self.textboxes[-1][key], self.default_values[key])
        for key in self.buttons[-1]:
            MyWindows.validate(self.textboxes[-1][key], lambda x: self.buttons[-1][key].configure(background=x.get()))

    def addTab(self):
        Notebook.Notebook.addTab(self)
        self.loadDefaultValues()

    def frameGenerator(self, parent, remove, disable):
        frame = Tkinter.Frame(parent)
        textboxes, disable_var, buttons = self.textboxes[-1], self.disable_vars[-1], self.buttons[-1]
        textboxes["Freq"] = MyWindows.newTextBox(frame, "Freq", validatefunction=lambda x: self.validateFreq(x))
        textboxes["Delay"] = MyWindows.newTextBox(frame, "Delay", 2)
        Tkinter.Button(frame, text="Disable", command=lambda: disable(disable_var, textboxes, buttons)).grid(row=0, column=4, padx=5, pady=5)
        Tkinter.Button(frame, text="Delete", command=remove).grid(row=0, column=5, padx=5, pady=5)
        textboxes["Width"] = MyWindows.newTextBox(frame, "Width", row=1)
        textboxes["Height"] = MyWindows.newTextBox(frame, "Height", 2, 1)
        textboxes["Color1"], buttons["Color1"] = MyWindows.newColorButton(frame, "Color1", 4, 1)
        textboxes["x"] = MyWindows.newTextBox(frame, "x", row=2)
        textboxes["y"] = MyWindows.newTextBox(frame, "y", 2, 2)
        textboxes["Color2"], buttons["Color2"] = MyWindows.newColorButton(frame, "Color2", 4, 2)
        return frame

    def validateFreq(self, textbox):
        target_freq = float(textbox.get())
        monitor_freq = int(self.frequency_textbox.get())
        freq_on = math.floor(monitor_freq/target_freq/2)
        freq_off = math.ceil(monitor_freq/target_freq/2)
        MyWindows.updateTextbox(textbox, float(monitor_freq)/(freq_off+freq_on))

    def loadValues(self, values):
        Notebook.Notebook.loadValues(self, values)
        for key in self.buttons[-1]:
            MyWindows.validateButtonColor(self.buttons[-1][key], self.textboxes[-1][key])

    def defaultDisability(self):
        for i in range(2, self.tab_count+1):
            MyWindows.updateVar(self.disable_vars[i], 1)
        self.disableTabs()