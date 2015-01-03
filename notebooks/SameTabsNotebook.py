__author__ = 'Anti'

from widgets import Frame
from frames import ExtractionPlotTabs, TargetsTab
import ttk


class SameTabsNotebook(Frame.Frame):
    def __init__(self, name, row, column, columnspan, padx, pady):
        Frame.Frame.__init__(self, name, row, column, columnspan, padx, pady)
        self.tabs = []
        self.tab_count = 0
        self.default_tab_count = 1

    def tabChangedEvent(self, event):
        if event.widget.index("current") == self.tab_count+1:
            self.addTab()

    def createWidget(self, parent):
        self.widget = ttk.Notebook(parent)
        self.widget.bind("<<NotebookTabChanged>>", self.tabChangedEvent)
        return self.widget

    def addInitialTabs(self):
        self.addPlusTab()
        self.widget.tab(self.tab_count, text="All")
        self.addPlusTab()

    def newTab(self):
        raise NotImplementedError("newTab not implemented!")

    def addPlusTab(self):
        self.tabs.append(self.newTab())
        self.tabs[-1].create(self.widget)
        self.widget.add(self.tabs[-1].widget, text="+")

    def loadDefaultValue(self):
        self.addInitialTabs()
        self.tabs[0].loadDefaultValue()  # Default values to All tab
        for _ in range(self.default_tab_count):
            self.addTab()

    def loadTab(self, tab_id, file):
        self.tabs[tab_id].load(file)

    def save(self, file):
        file.write(str(self.tab_count)+"\n")
        for tab_id in range(self.tab_count-1) :
            self.tabs[tab_id].save(file)

    def load(self, file):
        self.deleteAllTabs()
        tab_count = int(file.readline())
        self.loadTab(self.tab_count, file)  # Values to All tab
        for i in range(tab_count):
            self.addTab()
            self.loadTab(self.tab_count, file)

    def deleteAllTabs(self):
        if self.tab_count != 0:
            self.widget.select(1)
            while self.tab_count > 0:
                self.deleteTab()

    def deleteTab(self):
        current = self.widget.index("current")
        if current != 0:
            self.tab_count -= 1
            self.changeActiveTab(current)
            self.widget.forget(current)

    def changeActiveTab(self, current):
        if current == self.tab_count+1:
            self.widget.select(current-1)
        else:
            while current < self.tab_count+2:
                self.widget.tab(current, text=self.widget.tab(current, "text")-1)
                current += 1

    def addTab(self):
        self.tab_count += 1
        self.tabs[-1].loadDefaultValue()
        self.widget.tab(self.tab_count, text=self.tab_count)
        self.addPlusTab()


class ExtractionNotebook(SameTabsNotebook):
    def __init__(self, row, column, columnspan, padx, pady):
        SameTabsNotebook.__init__(self, "ExtractionNotebook", row, column, columnspan, padx, pady)

    def newTab(self):
        return ExtractionPlotTabs.ExtractionTab(0, 0, 1, 0, 0, self.deleteTab)


class PlotNotebook(SameTabsNotebook):
    def __init__(self, row, column, columnspan, padx, pady):
        SameTabsNotebook.__init__(self, "PlotNotebook", row, column, columnspan, padx, pady)

    def newTab(self):
        return ExtractionPlotTabs.ExtractionTab(0, 0, 1, 0, 0, self.deleteTab)


class TargetNotebook(SameTabsNotebook):
    def __init__(self, row, column, columnspan, padx, pady, validate_freq):
        SameTabsNotebook.__init__(self, "TargetNotebook", row, column, columnspan, padx, pady)
        self.validate_freq = validate_freq

    def newTab(self):
        return TargetsTab.TargetsTab(0, 0, 1, 0, 0, self.deleteTab, self.validate_freq)
