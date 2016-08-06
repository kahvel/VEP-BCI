from gui_elements.widgets.frames.notebooks import Notebook


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
        if self.hasTabs():
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

    def hasTabs(self):
        return self.tab_count != -1

    def getValue(self):
        return {i+1: widget.getValue() for i, widget in enumerate(self.widgets_list) if not widget.disabled}

    def tabDefaultValues(self, tab_index):
        self.widgets_list[tab_index].loadDefaultValue()

    def deleteAllTabs(self):
        if self.hasTabs():
            self.widget.select(0)
            while self.tab_count > 0:
                self.deleteTab()
