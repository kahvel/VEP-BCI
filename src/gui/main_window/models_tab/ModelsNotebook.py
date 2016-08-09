from gui_elements.widgets.frames.notebooks import EventNotebook
import ModelsNotebookTab
import constants as c


class ModelsNotebook(EventNotebook.EventNotebook):
    def __init__(self, parent, row, column, **kwargs):
        EventNotebook.EventNotebook.__init__(self, parent, c.MODELS_NOTEBOOK, row, column, **kwargs)
        self.tab_to_fill = None

    def addNewModelTabEvent(self):
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.addNewModelTabEvent())
        self.addNewTabToFill()
        return c.STOP_EVENT_SENDING

    def sendTabRemovedEvent(self, current_tab):
        self.sendEventToAll(lambda x: x.modelTabRemovedEvent(current_tab))

    def modelReceivedEvent(self, model):
        """
        Since currently tab frames do not know their number we have to send the event to only the correct tab.
        :param results:
        :return:
        """
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.modelReceivedEvent(model))
        return c.STOP_EVENT_SENDING

    def newTab(self, deleteTab):
        return ModelsNotebookTab.ModelsNotebookTab(self, deleteTab)

    def loadModelEvent(self, directory):
        self.widgets_list[self.tab_to_fill].sendEventToChildren(lambda x: x.loadModelEvent(directory))
        self.addNewTabToFill()
        return c.STOP_EVENT_SENDING
