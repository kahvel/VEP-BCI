__author__ = 'Anti'

from widgets import Frame
import ttk


class SameTabsNotebook(Frame.Frame):
    def __init__(self, name, row, column, columnspan, padx, pady, tab_template):
        Frame.Frame.__init__(self, name, row, column, columnspan, padx, pady)
        self.tab_template = tab_template
        self.tabs = []
        self.tab_count = 0
        self.default_tab_count = 1

    def tabChangedEvent(self, event):
        if event.widget.index("current") == self.tab_count+1:
            self.addTab()

    def createWidget(self, parent):
        self.widget = ttk.Notebook(parent)
        self.widget.bind("<<NotebookTabChanged>>", self.tabChangedEvent)
        #self.addInitialTabs()
        return self.widget

    def addInitialTabs(self):
        self.addPlusTab()
        self.widget.tab(self.tab_count, text="All")
        self.addPlusTab()

    def addPlusTab(self):
        self.tabs.append(self.tab_template(0, 0, 1, 0, 0, self.deleteTab))
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

    def deleteTab(self, var=None):
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