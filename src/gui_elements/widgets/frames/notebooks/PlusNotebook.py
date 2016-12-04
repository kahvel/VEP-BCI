import SameTabsNotebook
import constants as c


class PlusNotebook(SameTabsNotebook.SameTabsNotebook):
    def __init__(self, parent, name, row, column, **kwargs):
        SameTabsNotebook.SameTabsNotebook.__init__(self, parent, name, row, column, **kwargs )
        self.widget.bind("<<NotebookTabChanged>>", self.tabChangedEvent)

    def tabChangedEvent(self, event):
        if event.widget.index("current") == self.tab_count+1:
            self.plusTabClicked()
            self.tabDefaultValues(-1)

    def addInitialTabs(self):
        self.last_tab = self.addTab("+")
        self.plusTabClicked()

    def loadDefaultValue(self):
        SameTabsNotebook.SameTabsNotebook.loadDefaultValue(self)
        self.addInitialTabs()
        for i in range(self.tab_count+1):
            self.tabDefaultValues(i)

    def saveBciSettingsEvent(self, file):
        file.write(str(self.tab_count)+"\n")
        SameTabsNotebook.SameTabsNotebook.saveBciSettingsEvent(self, file)

    def loadBciSettingsEvent(self, file):
        if self.tab_count == -1:
            self.addInitialTabs()
        self.deleteAllTabs()
        tab_count = int(file.readline())
        for i in range(tab_count):
            self.plusTabClicked()
        SameTabsNotebook.SameTabsNotebook.loadBciSettingsEvent(self, file)

    def plusTabClicked(self):
        self.tab_count += 1
        self.widgets_list.append(self.last_tab)
        self.widget.tab(self.tab_count, text=self.tab_count+1)
        self.last_tab = self.addTab(c.PLUS_TAB)
