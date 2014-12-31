__author__ = 'Anti'

import ttk
import Tkinter
import MyWindows
import math
from main_logic import PSDAExtraction, CCAExtraction, CCAPSDAExtraction


class Notebook(ttk.Notebook):
    def __init__(self, parent):
        ttk.Notebook.__init__(self, parent)
        self.empty_tab = None
        self.tab_count = 0
        self.disable_vars = []
        self.vars = []
        self.textboxes = []
        self.checkboxes = []
        self.buttons = []
        self.bind("<<NotebookTabChanged>>", self.tabChangedEvent)

    def addInitialTabs(self):
        self.addPlusTab()
        self.addListElement()
        self.frameGenerator(self.empty_tab, self.removeTab, self.disableButtonPressed).pack()
        self.tab(self.tab_count, text="All")
        self.addPlusTab()

    def addPlusTab(self):
        self.empty_tab = Tkinter.Frame(self)
        self.add(self.empty_tab, text="+")

    def frameGenerator(self, parent, remove, disable):
        raise NotImplementedError("frameGenerator not implemented!")

    def removeListElement(self, i):
        del self.disable_vars[i]
        del self.vars[i]
        del self.textboxes[i]
        del self.buttons[i]
        del self.checkboxes[i]

    def addListElement(self):
        self.vars.append({})
        self.textboxes.append({})
        self.disable_vars.append(Tkinter.IntVar())
        self.buttons.append({})
        self.checkboxes.append({})

    def loadValues(self, values):
        MyWindows.updateDict(self.textboxes[-1], values[0].split(), MyWindows.updateTextbox)
        MyWindows.updateDict(self.vars[-1], values[1].split(), MyWindows.updateVar)
        MyWindows.updateVar(self.disable_vars[-1], values[2].split(":")[1])

    def save(self, file):
        file.write(str(self.tab_count)+"\n")
        for textboxes, vars, disable_var in zip(self.textboxes, self.vars, self.disable_vars):
            MyWindows.saveDict(textboxes, file, end=";")
            MyWindows.saveDict(vars, file, end=";")
            file.write("Disable:"+str(disable_var.get())+"\n")

    def load(self, file):
        self.removeAllTabs()
        tab_count = int(file.readline())
        self.loadValues(file.readline().split(";"))  # Values to All tab
        for i in range(tab_count):
            self.addTab()
            self.loadValues(file.readline().split(";"))
        self.disableTabs()

    def disableTabs(self):
        for i in range(self.tab_count+1):
            self.disableButtonChange(self.disable_vars[i], self.textboxes[i], self.buttons[i])

    def removeAllTabs(self):
        if self.tab_count != 0:
            self.select(1)
            while self.tab_count > 0:
                self.removeTab()

    def removeTab(self):
        current = self.index("current")
        if current != 0:
            self.tab_count -= 1
            self.removeListElement(current)
            self.updateTabs(current)
            self.forget(current)

    def updateTabs(self, current):
        if current == self.tab_count+1:
            self.select(current-1)
        else:
            while current < self.tab_count+2:
                self.tab(current, text=self.tab(current, "text")-1)
                current += 1

    def addTab(self):
        self.tab_count += 1
        self.addListElement()
        self.frameGenerator(self.empty_tab, self.removeTab, self.disableButtonPressed).pack()
        self.tab(self.tab_count, text=self.tab_count)
        self.addPlusTab()

    def tabChangedEvent(self, event):
        if event.widget.index("current") == self.tab_count+1:
            self.addTab()

    def disableButtonPressed(self, disable_var, textboxes=(), buttons=(), checkboxes=()):
        if disable_var.get() == 1:
            disable_var.set(0)
        else:
            disable_var.set(1)
        self.disableButtonChange(disable_var, textboxes, buttons, checkboxes)

    def disableButtonChange(self, disable_var, textboxes=(), buttons=(), checkboxes=()):
        if disable_var.get() == 1:
            textbox_state = "readonly"
            button_state = "disabled"
            checkbox_state = "disabled"
        else:
            textbox_state = Tkinter.NORMAL
            button_state = Tkinter.NORMAL
            checkbox_state = Tkinter.NORMAL
        self.disableDict(textboxes, textbox_state)
        self.disableDict(buttons, button_state)
        self.disableDict(checkboxes, checkbox_state)

    # def disableList(self, list, state):
    #     for item in list:
    #         item.config(state=state)

    def disableDict(self, dict, state):
        for key in dict:
            dict[key].config(state=state)

    # def disable(self, iterable, state):
    #     if isinstance(iterable, dict):
    #         self.disableDict(iterable, state)
    #     else:
    #         self.disableList(iterable, state)


class TargetNotebook(Notebook):
    def __init__(self, parent, frequency_textbox):
        Notebook.__init__(self, parent)
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
            MyWindows.changeButtonColor(self.buttons[-1][key], self.textboxes[-1][key])

    def addTab(self):
        Notebook.addTab(self)
        self.loadDefaultValues()

    def frameGenerator(self, parent, remove, disable):
        frame = Tkinter.Frame(parent)
        textboxes, disable_var, buttons = self.textboxes[-1], self.disable_vars[-1], self.buttons[-1]
        textboxes["Freq"] = MyWindows.newTextBox(frame, "Freq", validatecommand=self.validateFreq)
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
        if textbox.get() != "":
            monitor_freq = int(self.frequency_textbox.get())
            freq = float(textbox.get())
            freq_on = math.floor(monitor_freq/freq/2)
            freq_off = math.ceil(monitor_freq/freq/2)
            MyWindows.updateTextbox(textbox, float(monitor_freq)/(freq_off+freq_on))
        return True

    def loadValues(self, values):
        Notebook.loadValues(self, values)
        for key in self.buttons[-1]:
            MyWindows.changeButtonColor(self.buttons[-1][key], self.textboxes[-1][key])

    def defaultDisability(self):
        for i in range(2, self.tab_count+1):
            MyWindows.updateVar(self.disable_vars[i], 1)
        self.disableTabs()


class ExctractionNotebook(Notebook):
    def __init__(self, parent):
        Notebook.__init__(self, parent)
        self.classes = []
        self.addInitialTabs()

    def addListElement(self):
        Notebook.addListElement(self)
        self.classes.append({"PSDA": {}, "CCA": {}, "Both": {}})

    def removeListElement(self, i):
        Notebook.removeListElement(self, i)
        self.closeAllWindows(self.classes[i])
        del self.classes[i]

    def frameGenerator(self, parent, remove, disable):
        frame = Tkinter.Frame(parent)
        classes, vars, textboxes, disable_var, checkboxes, buttons = \
            self.classes[-1], self.vars[-1], self.textboxes[-1], self.disable_vars[-1], self.checkboxes[-1], self.buttons[-1]
        self.checkboxFrame(frame, vars, checkboxes).grid(columnspan=5)
        MyWindows.initButtonFrame(frame, ["PSDA", "Sum PSDA", "CCA", "Both", "Sum Both"],
                                  [lambda: self.createInstance(PSDAExtraction, classes["PSDA"], "Multiple"),
                                   lambda: self.createInstance(PSDAExtraction, classes["PSDA"], "Single"),
                                   lambda: self.createInstance(CCAExtraction, classes["CCA"], "Single"),
                                   lambda: self.createInstance(CCAPSDAExtraction, classes["Both"], "Multiple"),
                                   lambda: self.createInstance(CCAPSDAExtraction, classes["Both"], "Single")],
                                  row=1, buttons=buttons)
        self.initOptionsFrame(frame, vars, textboxes, checkboxes, buttons).grid(columnspan=5)
        Tkinter.Button(frame, text="Disable", command=lambda: disable(disable_var, textboxes, buttons, checkboxes)).grid(column=0, row=5)
        Tkinter.Button(frame, text="Remove", command=remove).grid(column=1, row=5)
        return frame

    def createInstance(self, file, classes, object):
        classes[object] = getattr(file, object)()
        classes[object].protocol("WM_DELETE_WINDOW", lambda: self.closeWindow(classes, object))

    def closeAllWindows(self, classes):
        for key in classes:
            for key2 in classes[key]:
                self.closeWindow(classes[key], key2)

    def closeWindow(self, classes, object):
        self.closeGenerators(classes[object].generators)
        classes[object].destroy()

    def closeGenerators(self, generators):
        for generator in generators:
            generator.close()

    def checkboxFrame(self, parent, vars, checkboxes):
        frame = Tkinter.Frame(parent)
        for i in range(len(MyWindows.sensor_names)):
            vars[str(i)], checkboxes[i] = MyWindows.newCheckbox(frame, MyWindows.sensor_names[i], column=i % 7, row=i//7, columnspan=1, padx=0, pady=0)
        return frame

    def initOptionsFrame(self, parent, vars, textboxes, checkboxes, buttons):
        frame = Tkinter.Frame(parent)
        vars["Normalise"], checkboxes["Normalise"] = MyWindows.newCheckbox(frame, "Normalise")
        vars["Detrend"], checkboxes["Detrend"] = MyWindows.newCheckbox(frame, "Detrend", column=2)
        vars["Filter"], checkboxes["Filter"] = MyWindows.newCheckbox(frame, "Filter", column=4)
        textboxes["Step"] = MyWindows.newTextBox(frame, "Step", row=1)
        textboxes["Length"] = MyWindows.newTextBox(frame, "Length", 2, 1)
        vars["Window"] = Tkinter.StringVar()
        vars["Window"].set("None") # TODO
        buttons["OptionMenu"] = Tkinter.OptionMenu(frame, vars["Window"], "None", "hanning", "hamming", "blackman", "kaiser", "bartlett")
        buttons["OptionMenu"].grid(column=0, row=4, padx=5, pady=5, columnspan=2)
        textboxes["From"] = MyWindows.newTextBox(frame, "From", row=3)
        textboxes["To"] = MyWindows.newTextBox(frame, "To", 2, 3)
        textboxes["Taps"] = MyWindows.newTextBox(frame, "Taps", 4, 3)
        textboxes["Arg"] = MyWindows.newTextBox(frame, "Arg", 2, 4)
        textboxes["Break"] = MyWindows.newTextBox(frame, "Break", 4, 4)
        return frame
