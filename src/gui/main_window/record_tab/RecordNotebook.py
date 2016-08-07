from gui_elements.widgets.frames.notebooks import SameTabsNotebook
import RecordNotebookTab
import constants as c


class RecordNotebook(SameTabsNotebook.SameTabsNotebook):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebook.SameTabsNotebook.__init__(self, parent, c.RECORD_NOTEBOOK, row, column, **kwargs)
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

    def trialEndedEvent(self):
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.trialEndedEvent())
        self.addNewTabToFill()
        return c.STOP_EVENT_SENDING

    def addNewTabToFill(self):
        self.addNewTab()
        self.tabDefaultValues(-1)
        self.tab_to_fill = self.tab_count

    def resultsReceivedEvent(self, results):
        """
        Since currently tab frames do not know their number we have to send the event to only the correct tab.
        :param results:
        :return:
        """
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.resultsReceivedEvent(results))
        return c.STOP_EVENT_SENDING

    def recordedEegReceivedEvent(self, eeg):
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.recordedEegReceivedEvent(eeg))
        return c.STOP_EVENT_SENDING

    def recordedFrequenciesReceivedEvent(self, frequencies):
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.recordedFrequenciesReceivedEvent(frequencies))
        return c.STOP_EVENT_SENDING

    def recordedFeaturesReceivedEvent(self, features):
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.recordedFeaturesReceivedEvent(features))
        return c.STOP_EVENT_SENDING

    def addNewTab(self):
        self.tab_count += 1
        self.widgets_list.append(self.addTab(self.tab_count+1))

    def newTab(self, deleteTab):
        return RecordNotebookTab.RecordNotebookTab(self, deleteTab)

    def saveBciSettingsEvent(self, file):
        SameTabsNotebook.SameTabsNotebook.saveBciSettingsEvent(self, file)
        return c.STOP_EVENT_SENDING

    def loadBciSettingsEvent(self, file):
        SameTabsNotebook.SameTabsNotebook.loadBciSettingsEvent(self, file)
        if not self.hasTabs():
            self.loadDefaultValue()
        return c.STOP_EVENT_SENDING

    def loadEegEvent(self, directory):
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.loadEegEvent(directory))
        self.addNewTabToFill()
        return c.STOP_EVENT_SENDING

    def deleteTab(self):
        """
        Do not allow to delete last tab (the one to be filled).
        :return:
        """
        current_tab = self.widget.index("current")
        if current_tab != self.tab_count:
            SameTabsNotebook.SameTabsNotebook.deleteTab(self)
            self.tab_to_fill -= 1
            self.sendEventToAll(lambda x: x.recordTabRemoved(current_tab))
