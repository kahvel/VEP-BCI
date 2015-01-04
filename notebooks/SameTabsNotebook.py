__author__ = 'Anti'

import ttk

from frames import ExtractionPlotTabs, TargetsTab, Frame


class SameTabsNotebook(Frame.Frame):
    def __init__(self, name, row, column, columnspan, padx, pady):
        Frame.Frame.__init__(self, name, row, column, columnspan, padx, pady)
        self.tab_count = 0
        self.default_tab_count = 1

    def tabChangedEvent(self, event):
        if event.widget.index("current") == self.tab_count+1:
            self.addTab()

    def createWidget(self, parent):
        self.widget = ttk.Notebook(parent)
        self.widget.bind("<<NotebookTabChanged>>", self.tabChangedEvent)
        self.addInitialTabs()
        return self.widget

    def addInitialTabs(self):
        self.addPlusTab()
        self.widget.tab(0, text="All")
        self.addPlusTab()

    def newTab(self):
        raise NotImplementedError("newTab not implemented!")

    def addPlusTab(self):
        self.widgets_list.append(self.newTab())
        self.widgets_list[-1].create(self.widget)
        self.widget.add(self.widgets_list[-1].widget, text="+")

    def loadDefaultValue(self):
        self.widgets_list[0].loadDefaultValue()  # Default values to All tab
        for _ in range(self.default_tab_count):
            self.addTab()

    def save(self, file):
        file.write(str(self.tab_count)+"\n")
        for widget in self.widgets_list[:-1]:
            widget.save(file)

    def load(self, file):
        self.deleteAllTabs()
        tab_count = int(file.readline())
        self.widgets_list[0].load(file)  # Values to All tab
        for i in range(tab_count):
            self.addTab()
            self.widgets_list[i+1].load(file)

    def deleteAllTabs(self):
        if self.tab_count != 0:
            self.widget.select(1)
            while self.tab_count > 0:
                self.deleteTab()

    def deleteTab(self):
        current = self.widget.index("current")
        if current != 0:
            del self.widgets_list[current]
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
        self.widgets_list[-1].loadDefaultValue()
        self.widget.tab(self.tab_count, text=self.tab_count)
        self.addPlusTab()


class ExtractionNotebook(SameTabsNotebook):
    def __init__(self, row, column, columnspan, padx, pady):
        SameTabsNotebook.__init__(self, "Extraction", row, column, columnspan, padx, pady)

    def newTab(self):
        return ExtractionPlotTabs.ExtractionTab(0, 0, 1, 0, 0, self.deleteTab)


class PlotNotebook(SameTabsNotebook):
    def __init__(self, row, column, columnspan, padx, pady):
        SameTabsNotebook.__init__(self, "Plot", row, column, columnspan, padx, pady)

    def newTab(self):
        return ExtractionPlotTabs.ExtractionTab(0, 0, 1, 0, 0, self.deleteTab)


class TargetNotebook(SameTabsNotebook):
    def __init__(self, row, column, columnspan, padx, pady, validate_freq):
        SameTabsNotebook.__init__(self, "Targets", row, column, columnspan, padx, pady)
        self.validate_freq = validate_freq

    def newTab(self):
        return TargetsTab.TargetsTab(0, 0, 1, 0, 0, self.deleteTab, self.validate_freq)
