from gui_elements.widgets.frames.tabs import DisableDeleteNotebookTab
import constants as c


class EegTab(DisableDeleteNotebookTab.Disable):
    def __init__(self, parent, **kwargs):
        DisableDeleteNotebookTab.Disable.__init__(self, parent, c.EMOTIV_TAB)
        self.addChildWidgets((
            self.getDisableButton(0, 0),
        ))
