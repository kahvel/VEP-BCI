from gui.widgets.frames.tabs import DisableDeleteNotebookTab, RecordTab
from gui.widgets import Textboxes, OptionMenu, Buttons
import Savable
import constants as c


class RecordNotebookTab(DisableDeleteNotebookTab.Delete, Savable.Savable):
    def __init__(self, parent, deleteTab, **kwargs):
        DisableDeleteNotebookTab.Delete.__init__(self, parent, c.RECORD_TAB, **kwargs)
        Savable.Savable.__init__(self)
        self.addChildWidgets((
            RecordNotebookTabFrame(self),
            self.getDeleteButton(1, 0, deleteTab),
        ))

    def fill(self, results):
        self.widgets_dict[c.RECORD_TAB].fill(results)


class RecordNotebookTabFrame(DisableDeleteNotebookTab.Disable, Savable.Savable):
    def __init__(self, parent, **kwargs):
        DisableDeleteNotebookTab.Disable.__init__(self, parent, c.RECORD_TAB, **kwargs)
        Savable.Savable.__init__(self)
        self.addChildWidgets((
            RecordTab.RecordTab(self),
            self.getDisableButton(1, 0),
        ))

    def fill(self, results):
        self.widgets_dict[c.RECORD_TAB].fill(results)
