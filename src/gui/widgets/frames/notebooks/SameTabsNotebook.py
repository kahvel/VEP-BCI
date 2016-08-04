from gui.widgets.frames.notebooks import Notebook
from gui.widgets.frames.tabs import RecordTab
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


class ResultsNotebook(SameTabsNotebook):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebook.__init__(self, parent, c.RESULTS_NOTEBOOK, row, column, **kwargs)
        self.tab_to_fill = None

    def loadDefaultValue(self):
        SameTabsNotebook.loadDefaultValue(self)
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
        self.addNewTab()
        self.tabDefaultValues(-1)
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.trialEndedEvent())
        self.tab_to_fill = self.tab_count
        return c.STOP_EVENT_SENDING

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
        return RecordTab.RecordTab(self, deleteTab)

    def saveBciSettingsEvent(self, file):
        SameTabsNotebook.saveBciSettingsEvent(self, file)
        return c.STOP_EVENT_SENDING

    def loadBciSettingsEvent(self, file):
        SameTabsNotebook.loadBciSettingsEvent(self, file)
        if not self.hasTabs():
            self.loadDefaultValue()
        return c.STOP_EVENT_SENDING

    def loadEegEvent(self, directory):
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.loadEegEvent(directory))
        self.addNewTab()
        self.tabDefaultValues(-1)
        self.tab_to_fill = self.tab_count
        return c.STOP_EVENT_SENDING
