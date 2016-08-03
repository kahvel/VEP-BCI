from gui.widgets.frames.notebooks import Notebook
from gui.widgets.frames.tabs import RecordNotebookTab
import constants as c


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


class ResultsNotebook(SameTabsNotebook):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebook.__init__(self, parent, c.RESULTS_NOTEBOOK, row, column, **kwargs)

    def trialEndedEvent(self):
        self.addTab(self.tab_count)

    def newTab(self, deleteTab):
        return RecordNotebookTab.RecordNotebookTab(self,)  # TODO

    def fillTab(self):
        pass
