__author__ = 'Anti'

import ttk
import Tkinter
from main_window import MyWindows


class Notebook(ttk.Notebook):
    def __init__(self, parent):
        ttk.Notebook.__init__(self, parent)
        self.empty_tab = None
        self.tab_count = 0
        self.default_tab_count = None
        self.disable_vars = []
        self.vars = []
        self.textboxes = []
        self.checkboxes = []
        self.buttons = []
        self.disabled_textboxes = []
        self.bind("<<NotebookTabChanged>>", self.tabChangedEvent)

    def addInitialTabs(self):
        self.addPlusTab()
        self.addListElement()
        self.fillFrame()
        self.tab(self.tab_count, text="All")
        self.addPlusTab()

    def addPlusTab(self):
        self.empty_tab = Tkinter.Frame(self)
        self.add(self.empty_tab, text="+")

    def fillFrame(self):
        self.frameGenerator(self.empty_tab).pack()
        disable_var, textboxes, buttons = self.disable_vars[-1], self.textboxes[-1], self.buttons[-1]
        MyWindows.newButtonFrame(self.empty_tab, ["Disable", "Delete"],
                                 [lambda: self.disableButtonPressed(disable_var, textboxes, buttons), self.removeTab]).pack()

    def frameGenerator(self, parent):
        raise NotImplementedError("frameGenerator not implemented!")

    def loadDefaultValues(self):
        raise NotImplementedError("loadDefaultValues not implemented!")

    def defaultDisability(self):
        raise NotImplementedError("defaultDisability not implemented!")

    def loadDefaultNotebook(self):
        self.loadDefaultValues()  # Default values to All tab
        for _ in range(self.default_tab_count):
            self.addTab()
        self.defaultDisability()

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
        self.fillFrame()
        self.tab(self.tab_count, text=self.tab_count)
        self.addPlusTab()
        self.loadDefaultValues()

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

    def disableDict(self, dict, state):
        for key in dict:
            if dict[key] not in self.disabled_textboxes:
                dict[key].config(state=state)
