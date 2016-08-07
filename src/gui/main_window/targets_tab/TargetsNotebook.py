from gui_elements.widgets.frames.notebooks import PlusNotebook
import TargetsNotebookTab
import constants as c


class TargetsNotebook(PlusNotebook.PlusNotebook):
    def __init__(self, parent, row, column, getMonitorFreq, **kwargs):
        PlusNotebook.PlusNotebook.__init__(self, parent, c.WINDOW_TAB_TARGETS_NOTEBOOK, row, column, **kwargs)
        self.getMonitorFreq = getMonitorFreq

    def plusTabClicked(self):  # Updates TargetChoosingMenus
        self.sendEventToAll(lambda x: x.targetAddedEvent())
        PlusNotebook.PlusNotebook.plusTabClicked(self)

    def getEnabledTabs(self):
        return list(tab.disabled for tab in self.widgets_list)

    def newTab(self, deleteTab):
        return TargetsNotebookTab.TargetsNotebookTab(self, self.getMonitorFreq, deleteTab, self.getEnabledTabs, self.getCurrentTab)

    def deleteTab(self):  # Updates TargetChoosingMenus
        deleted_tab = PlusNotebook.PlusNotebook.deleteTab(self)
        self.sendEventToAll(lambda x: x.targetRemovedEvent(deleted_tab))
