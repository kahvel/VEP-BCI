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


class ResultsNotebook(SameTabsNotebook, Savable.Loadable):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebook.__init__(self, parent, c.RESULTS_NOTEBOOK, row, column, **kwargs)
        Savable.Loadable.__init__(self)
        self.load_successful = False
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
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.fillResultsFrameEvent(results))

    def addNewTab(self):
        self.tab_count += 1
        self.widgets_list.append(self.addTab(self.tab_count+1))

    def newTab(self, deleteTab):
        return RecordTab.RecordTab(self, deleteTab)

    # def tabChangedEvent(self, event):
    #     if event.widget.index("current") == self.tab_count+1:
    #         self.askLoadFile()
    #         if not self.load_successful:
    #             self.changeActiveTab(self.getCurrentTab())
    #         else:
    #             self.addNewTab()
    #             self.tabDefaultValues(-1)
    #         self.load_successful = False

    def loadFromFile(self, file):
        # to stuff
        self.load_successful = True

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
        return c.STOP_EVENT_SENDING
