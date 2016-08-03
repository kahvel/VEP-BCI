from gui.widgets.frames.notebooks import Notebook
from gui.widgets.frames.tabs import RecordNotebookTab
import constants as c
import Savable


class SameTabsNotebook(Notebook.Notebook):
    def __init__(self, parent, name, row, column, **kwargs):
        Notebook.Notebook.__init__(self, parent, name, row, column, **kwargs)
        self.tab_count = -1
        self.last_tab = None

    def newTab(self, deleteTab):
        raise NotImplementedError("newTab not implemented!")

    def addTab(self, text):
        tab = self.newTab(self.deleteTab)
        self.widget.add(tab.widget, text=text)
        return tab

    def deleteTab(self):
        current = self.getCurrentTab()
        del self.widgets_list[current]
        self.tab_count -= 1
        if self.tab_count != -1:
            self.changeActiveTab(current)
        self.widget.forget(current)
        return current

    def getCurrentTab(self):
        return self.widget.index("current")

    def changeActiveTab(self, current):
        if current == self.tab_count+1:
            self.widget.select(current-1)
        else:
            while current < self.tab_count+2:
                self.widget.tab(current, text=self.widget.tab(current, "text")-1)
                current += 1

    def getValue(self):
        return {i+1: widget.getValue() for i, widget in enumerate(self.widgets_list) if not widget.disabled}

    def tabDefaultValues(self, tab_index):
        self.widgets_list[tab_index].loadDefaultValue()


class ResultsNotebook(SameTabsNotebook, Savable.Loadable):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebook.__init__(self, parent, c.RESULTS_NOTEBOOK, row, column, **kwargs)
        Savable.Loadable.__init__(self)
        self.widget.bind("<<NotebookTabChanged>>", self.tabChangedEvent)
        self.load_successful = False

    def loadDefaultValue(self):
        SameTabsNotebook.loadDefaultValue(self)
        self.addInitialTabs()
        for i in range(self.tab_count+1):
            self.tabDefaultValues(i)

    def addInitialTabs(self):
        self.last_tab = self.addTab("Load")
        self.trialEndedEvent()

    def trialEndedEvent(self):
        self.tab_count += 1
        self.widgets_list.append(self.last_tab)
        self.widget.tab(self.tab_count, text=self.tab_count+1)
        self.last_tab = self.addTab("Load")

    def newTab(self, deleteTab):
        return RecordNotebookTab.RecordNotebookTab(self, deleteTab)

    def fillTab(self):
        pass

    def tabChangedEvent(self, event):
        if event.widget.index("current") == self.tab_count+1:
            self.askLoadFile()
            if not self.load_successful:
                self.changeActiveTab(self.getCurrentTab())

    def loadFromFile(self, file):
        # to stuff
        self.load_successful = True
