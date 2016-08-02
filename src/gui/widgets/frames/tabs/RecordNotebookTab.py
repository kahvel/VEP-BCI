from gui.widgets.frames.tabs import DisableDeleteNotebookTab, RecordTab
from gui.widgets import Textboxes, OptionMenu, Buttons
import Savable
import constants as c


class RecordNotebookTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab, Savable.Savable):
    def __init__(self, parent, buttons, deleteTab, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.RECORD_TAB, **kwargs)
        Savable.Savable.__init__(self)
        self.addChildWidgets((
            RecordTab.RecordTab(self, buttons),
            self.getDisableDeleteFrame(1, 0, deleteTab),
        ))
