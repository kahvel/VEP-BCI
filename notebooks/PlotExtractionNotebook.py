__author__ = 'Anti'

import Notebook
import Tkinter
from main_window import MyWindows


class PlotExtractionNotebook(Notebook.Notebook):
    def __init__(self, parent):
        Notebook.Notebook.__init__(self, parent)
        self.default_tab_count = 1
        self.windows = []
        self.addInitialTabs()

    def removeListElement(self, i):
        Notebook.Notebook.removeListElement(self, i)
        self.closeAllWindows(self.windows[i])
        del self.windows[i]

    def loadDefaultValues(self):
        MyWindows.updateTextbox(self.textboxes[-1]["Step"], 32)
        MyWindows.updateTextbox(self.textboxes[-1]["Length"], 512)
        MyWindows.updateVar(self.vars[-1]["6"], 1)
        MyWindows.updateVar(self.vars[-1]["7"], 1)
        MyWindows.updateVar(self.vars[-1]["Window"], "None")
        MyWindows.updateTextbox(self.textboxes[-1]["Beta"], 0)
        MyWindows.updateTextbox(self.textboxes[-1]["From"], 0)
        MyWindows.updateTextbox(self.textboxes[-1]["To"], 0)
        MyWindows.updateTextbox(self.textboxes[-1]["Taps"], 0)
        MyWindows.updateTextbox(self.textboxes[-1]["Break"], 0)
        self.disableTextboxes(self.vars[-1]["Filter"], self.textboxes[-1], ["From", "To", "Taps"], 1)
        self.disableTextboxes(self.vars[-1]["Window"], self.textboxes[-1], ["Beta"], "Kaiser")

    def defaultDisability(self):
        pass  # Already have all tabs enabled

    def buttonFrame(self, frame, windows, buttons):
        raise NotImplementedError("buttonFrame not implemented!")

    def frameGenerator(self, parent, remove, disable):
        frame = Tkinter.Frame(parent)
        windows, vars, textboxes, disable_var, checkboxes, buttons = \
            self.windows[-1], self.vars[-1], self.textboxes[-1], self.disable_vars[-1], self.checkboxes[-1], self.buttons[-1]
        self.checkboxFrame(frame, vars, checkboxes).grid(columnspan=5)
        self.buttonFrame(frame, windows, buttons)
        self.optionsFrame(frame, vars, textboxes, checkboxes, buttons).grid(columnspan=5)
        Tkinter.Button(frame, text="Disable", command=lambda: disable(disable_var, textboxes, buttons, checkboxes)).grid(column=0, row=6)
        Tkinter.Button(frame, text="Delete", command=remove).grid(column=1, row=6)
        return frame

    def createWindow(self, file, windows, object):
        windows[object] = getattr(file, object)()
        windows[object].protocol("WM_DELETE_WINDOW", lambda: self.closeWindow(windows, object))

    def closeAllWindows(self, windows):
        for key in windows:
            for key2 in windows[key]:
                self.closeWindow(windows[key], key2)

    def closeWindow(self, windows, object):
        windows[object].close()

    def checkboxFrame(self, parent, vars, checkboxes):
        frame = Tkinter.Frame(parent)
        for i in range(len(MyWindows.sensor_names)):
            vars[str(i)], checkboxes[i] = MyWindows.newCheckbox(frame, MyWindows.sensor_names[i], column=i % 7, row=i//7, columnspan=1, padx=0, pady=0)
        return frame

    def optionsFrame(self, parent, vars, textboxes, checkboxes, buttons):
        frame = Tkinter.Frame(parent)
        vars["Normalise"], checkboxes["Normalise"] = MyWindows.newCheckbox(frame, "Normalise")
        vars["Detrend"], checkboxes["Detrend"] = MyWindows.newCheckbox(frame, "Detrend", column=2)
        vars["Filter"], checkboxes["Filter"] = MyWindows.newCheckbox(frame, "Filter", column=4, command=lambda: self.disableTextboxes(vars["Filter"], textboxes, ["From", "To", "Taps"], 1))
        textboxes["Step"] = MyWindows.newTextBox(frame, "Step", row=1)
        textboxes["Length"] = MyWindows.newTextBox(frame, "Length", 2, 1)
        vars["Window"], buttons["OptionMenu"] = MyWindows.newOptionMenu(frame, ("None", "Hanning", "Hamming", "Blackman", "Kaiser", "Bartlett"), row=4, command=lambda x: self.disableTextboxes(vars["Window"], textboxes, ["Beta"], "Kaiser"))
        textboxes["From"] = MyWindows.newTextBox(frame, "From", row=3)
        textboxes["To"] = MyWindows.newTextBox(frame, "To", 2, 3)
        textboxes["Taps"] = MyWindows.newTextBox(frame, "Taps", 4, 3)
        textboxes["Beta"] = MyWindows.newTextBox(frame, "Beta", 2, 4)
        textboxes["Break"] = MyWindows.newTextBox(frame, "Break", 4, 4)
        return frame

    def disableTextbox(self, textbox):
        textbox.config(state="readonly")
        self.disabled_textboxes.append(textbox)

    def enableTextbox(self, textbox):
        textbox.config(state=Tkinter.NORMAL)
        self.disabled_textboxes.remove(textbox)

    def disableTextboxes(self, var, textboxes, keys, value):
        function = self.enableTextbox if var.get() == value else self.disableTextbox
        for key in keys:
            function(textboxes[key])

    def disableAllTextboxes(self):
        for i in range(self.tab_count):
            self.disableTextboxes(self.vars[i]["Filter"], self.textboxes[i], ["From", "To", "Taps"], 1)
            self.disableTextboxes(self.vars[i]["Window"], self.textboxes[i], ["Beta"], "Kaiser")

    def load(self, file):
        Notebook.Notebook.load(self, file)
        self.disableAllTextboxes()

