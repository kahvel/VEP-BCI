from gui_elements.widgets.frames.notebooks import EventNotebook
import RecordNotebookTab
import constants as c


class RecordNotebook(EventNotebook.EventNotebook):
    def __init__(self, parent, row, column, **kwargs):
        EventNotebook.EventNotebook.__init__(self, parent, c.RECORD_NOTEBOOK, row, column, **kwargs)
        self.tab_to_fill = None

    def getRecordingNotebookWidgetsEvent(self):
        self.sendEventToAll(lambda x: x.sendRecordingNotebookWidgetsEvent(self.widgets_list))

    def addNewRecordingTabEvent(self):
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.addNewRecordingTabEvent())
        self.addNewTabToFill()
        return c.STOP_EVENT_SENDING

    def sendTabRemovedEvent(self, current_tab):
        self.sendEventToAll(lambda x: x.recordTabRemovedEvent(current_tab))

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

    def newTab(self, deleteTab):
        return RecordNotebookTab.RecordNotebookTab(self, deleteTab)

    def saveBciSettingsEvent(self, file):
        EventNotebook.EventNotebook.saveBciSettingsEvent(self, file)
        return c.STOP_EVENT_SENDING

    def loadBciSettingsEvent(self, file):
        EventNotebook.EventNotebook.loadBciSettingsEvent(self, file)
        if not self.hasTabs():
            self.loadDefaultValue()
        return c.STOP_EVENT_SENDING

    def loadEegEvent(self, directory):
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.loadEegEvent(directory))
        self.addNewTabToFill()
        return c.STOP_EVENT_SENDING
