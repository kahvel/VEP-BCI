from gui_elements.widgets.frames.notebooks import SameTabsNotebook
import constants as c


class EventNotebook(SameTabsNotebook.SameTabsNotebook):
    def __init__(self, parent, name, row, column, **kwargs):
        SameTabsNotebook.SameTabsNotebook.__init__(self, parent, name, row, column, **kwargs)
        self.tab_to_fill = None

    def loadDefaultValue(self):
        SameTabsNotebook.SameTabsNotebook.loadDefaultValue(self)
        self.addInitialTabs()
        for i in range(self.tab_count+1):
            self.tabDefaultValues(i)
        self.tab_to_fill = 0

    def getValue(self):
        for i, widget in enumerate(self.widgets_list):
            if not widget.disabled and i == self.tab_to_fill:
                return widget.getValue()

    def addInitialTabs(self):
        self.addNewTab()

    def sendTabRemovedEvent(self, current_tab):
        raise NotImplementedError("sendTabRemovedEvent not implemented")

    def addNewTabToFill(self):
        self.addNewTab()
        self.tabDefaultValues(-1)
        self.tab_to_fill = self.tab_count

    def addNewTab(self):
        self.tab_count += 1
        self.widgets_list.append(self.addTab(self.tab_count+1))

    def deleteTab(self):
        """
        Do not allow to delete last tab (the one to be filled).
        :return:
        """
        current_tab = self.widget.index("current")
        if current_tab != self.tab_count:
            SameTabsNotebook.SameTabsNotebook.deleteTab(self)
            self.tab_to_fill -= 1
            self.sendTabRemovedEvent(current_tab)

    def saveBciSettingsEvent(self, file):
        SameTabsNotebook.SameTabsNotebook.saveBciSettingsEvent(self, file)
        return c.STOP_EVENT_SENDING

    def loadBciSettingsEvent(self, file):
        SameTabsNotebook.SameTabsNotebook.loadBciSettingsEvent(self, file)
        if not self.hasTabs():
            self.loadDefaultValue()
        return c.STOP_EVENT_SENDING
