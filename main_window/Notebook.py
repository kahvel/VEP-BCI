__author__ = 'Anti'

import ttk
import Tkinter
import MyWindows
import math
from main_logic import PSDAExtraction, CCAExtraction, CCAPSDAExtraction


class Notebook(ttk.Notebook):
    def __init__(self, parent):
        ttk.Notebook.__init__(self, parent)
        self.add_tab = None
        self.tab_count = 0
        self.bind("<<NotebookTabChanged>>", self.tabChangedEvent)

    def addAllTab(self):
        self.add(self.frameGenerator(self.add_tab, self.removeTab), text="All")

    def addPlusTab(self):
        self.add_tab = Tkinter.Frame(self)
        self.add(self.add_tab, text="+")

    def frameGenerator(self, parent, remove):
        raise NotImplementedError("frameGenerator not implemented!")

    def removeTab(self):
        current = self.index("current")
        if current != 0:
            self.tab_count -= 1
            self.updateTabs(current)
            self.forget(current)
            return True
        else:
            return False

    def updateTabs(self, current):
        if current == self.tab_count+1:
            self.select(current-1)
        else:
            while current < self.tab_count+2:
                self.tab(current, text=self.tab(current, "text")-1)
                current += 1

    def addTab(self):
        self.tab_count += 1
        self.frameGenerator(self.add_tab, self.removeTab).pack()
        self.tab(self.tab_count, text=self.tab_count)
        self.addPlusTab()

    def tabChangedEvent(self, event):
        if event.widget.index("current") == self.tab_count+1:
            self.addTab()


class TargetNotebook(Notebook):
    def __init__(self, parent, target_textboxes, disable_vars, target_color_buttons, frequency_textbox):
        Notebook.__init__(self, parent)
        self.frequency_textbox = frequency_textbox
        self.target_textboxes = target_textboxes
        self.disable_vars = disable_vars
        self.target_color_buttons = target_color_buttons
        self.addAllTab()
        self.addPlusTab()
        self.default_values = {"Height": 150,
                               "Width": 150,
                               "x": 0,
                               "y": 0,
                               "Freq": 10.0,
                               "Color1": "#ffffff",
                               "Color2": "#777777",
                               "Delay": 0}

    def addTarget(self):
        self.target_textboxes.append({})
        self.disable_vars.append(Tkinter.IntVar())
        self.target_color_buttons.append({})
        return self.target_textboxes[-1], self.disable_vars[-1], self.target_color_buttons[-1]

    def loadDefaultValues(self):
        for key in self.default_values:
            MyWindows.updateTextbox(self.target_textboxes[-1][key], self.default_values[key])
        for key in self.target_color_buttons[-1]:
            MyWindows.changeButtonColor(self.target_color_buttons[-1][key], self.target_textboxes[-1][key])

    def removeEvent(self, i):
        del self.target_textboxes[i]
        del self.target_color_buttons[i]
        del self.disable_vars[i]

    def addTab(self):
        Notebook.addTab(self)
        self.loadDefaultValues()

    def removeTab(self):
        i = self.index("current")  # Notebook.removeTab changes index("current") value
        if Notebook.removeTab(self):
            self.removeEvent(i)

    def frameGenerator(self, parent, remove):
        frame = Tkinter.Frame(parent)
        textboxes, disable_var, color_buttons = self.addTarget()
        textboxes["Freq"] = MyWindows.newTextBox(frame, "Freq", 0, 0, validatecommand=self.validateFreq)
        textboxes["Delay"] = MyWindows.newTextBox(frame, "Delay", 2, 0)
        Tkinter.Button(frame, text="Disable", command=lambda: self.disableButtonPressed(textboxes, disable_var, color_buttons)).grid(row=0, column=4, padx=5, pady=5)
        Tkinter.Button(frame, text="Delete", command=remove).grid(row=0, column=5, padx=5, pady=5)
        textboxes["Width"] = MyWindows.newTextBox(frame, "Width", 0, 1)
        textboxes["Height"] = MyWindows.newTextBox(frame, "Height", 2, 1)
        textboxes["Color1"] = MyWindows.newColorButton(4, 1, frame, "Color1", textboxes, color_buttons)
        textboxes["x"] = MyWindows.newTextBox(frame, "x", 0, 2)
        textboxes["y"] = MyWindows.newTextBox(frame, "y", 2, 2)
        textboxes["Color2"] = MyWindows.newColorButton(4, 2, frame, "Color2", textboxes, color_buttons)
        return frame

    def validateFreq(self, textbox):
        if textbox.get() != "":
            monitor_freq = int(self.frequency_textbox.get())
            freq = float(textbox.get())
            freq_on = math.floor(monitor_freq/freq/2)
            freq_off = math.ceil(monitor_freq/freq/2)
            MyWindows.updateTextbox(textbox, float(monitor_freq)/(freq_off+freq_on))
        return True

    def disableButtonPressed(self, textboxes, disable_var, color_buttons):
        if disable_var.get() == 1:
            disable_var.set(0)
        else:
            disable_var.set(1)
        self.disableButtonChange(textboxes, disable_var, color_buttons)

    def disableButtonChange(self, textboxes, disable_var, color_buttons):
        if disable_var.get() == 1:
            textbox_state = "readonly"
            button_state = "disabled"
        else:
            textbox_state = Tkinter.NORMAL
            button_state = Tkinter.NORMAL
        for key in textboxes:
            textboxes[key].config(state=textbox_state)
        for key in color_buttons:
            color_buttons[key].config(state=button_state)


class ExctractionNotebook(Notebook):
    def __init__(self, parent, sensor_checkbox_vars):
        Notebook.__init__(self, parent)
        self.sensor_checkbox_vars = sensor_checkbox_vars
        self.classes = {"PSDA": {}, "CCA": {}, "CCA+PSDA": {}}
        self.addAllTab()
        self.addPlusTab()

    def frameGenerator(self, parent, remove):
        frame = Tkinter.Frame(parent)
        self.checkboxFrame(frame).grid(columnspan=5)
        MyWindows.initButtonFrame(frame, ["PSDA", "Sum PSDA", "CCA", "Both", "Sum Both"],
                                  [lambda: self.createInstance(PSDAExtraction, "PSDA", "Multiple"),
                                   lambda: self.createInstance(PSDAExtraction, "PSDA", "Single"),
                                   lambda: self.createInstance(CCAExtraction, "CCA", "Single"),
                                   lambda: self.createInstance(CCAPSDAExtraction, "Both", "Multiple"),
                                   lambda: self.createInstance(CCAPSDAExtraction, "Both", "Single")], row=1)
        return frame

    def createInstance(self, file, group, object):
        self.classes[group][object] = getattr(file, object)()
        self.classes[group][object].protocol("WM_DELETE_WINDOW", lambda: self.closeWindow(group, object))

    def closeWindow(self, group, object):
        self.closeGenerators(self.classes[group][object].generators)
        self.classes[group][object].destroy()
        self.classes[group][object] = None

    def closeGenerators(self, generators):
        for generator in generators:
            generator.close()

    def checkboxFrame(self, parent):
        frame = Tkinter.Frame(parent)
        for i in range(len(MyWindows.sensor_names)):
            self.sensor_checkbox_vars.append(Tkinter.IntVar())
            Tkinter.Checkbutton(frame, text=MyWindows.sensor_names[i],
                                variable=self.sensor_checkbox_vars[i]).grid(column=i % 7, row=i//7)
        return frame