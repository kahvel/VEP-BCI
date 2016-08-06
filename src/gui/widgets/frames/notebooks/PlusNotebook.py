from gui.widgets.frames.tabs import TargetsTab, ExtractionTab, PlotTab
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


class ExtractionNotebook(PlusNotebook):
    def __init__(self, parent, row, column, **kwargs):
        PlusNotebook.__init__(self, parent, c.EXTRACTION_NOTEBOOK, row, column, **kwargs)

    def newTab(self, deleteTab):
        return ExtractionTab.ExtractionTab(self, deleteTab)


class PlotNotebook(PlusNotebook):
    def __init__(self, parent, row, column, **kwargs):
        PlusNotebook.__init__(self, parent, c.MAIN_NOTEBOOK_PLOT_TAB, row, column, **kwargs)

    def newTab(self, deletaTab):
        return PlotTab.PlotTab(self, deletaTab)


class TargetNotebook(PlusNotebook):
    def __init__(self, parent, row, column, getMonitorFreq, **kwargs):
        PlusNotebook.__init__(self, parent, c.WINDOW_TAB_TARGETS_NOTEBOOK, row, column, **kwargs)
        self.getMonitorFreq = getMonitorFreq

    def plusTabClicked(self):  # Updates TargetChoosingMenus
        self.sendEventToRoot(lambda x: x.targetAddedEvent())
        PlusNotebook.plusTabClicked(self)

    def getEnabledTabs(self):
        return list(tab.disabled for tab in self.widgets_list)

    def newTab(self, deleteTab):
        return TargetsTab.TargetsTab(self, self.getMonitorFreq, deleteTab, self.getEnabledTabs, self.getCurrentTab)

    def deleteTab(self):  # Updates TargetChoosingMenus
        deleted_tab = PlusNotebook.deleteTab(self)
        self.sendEventToRoot(lambda x: x.targetRemovedEvent(deleted_tab))