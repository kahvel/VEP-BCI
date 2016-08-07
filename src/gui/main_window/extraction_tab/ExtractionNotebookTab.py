from gui_elements.widgets.frames.tabs import DisableDeleteNotebookTab
import ExtractionNotebookTabNotebook
import constants as c


class ExtractionNotebookTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, deleteTab, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.EXTRACTION_NOTEBOOK_TAB, **kwargs)
        self.addChildWidgets((
            ExtractionNotebookTabNotebook.ExtractionNotebookTabNotebook(self),
            self.getDisableDeleteFrame(3, 0, deleteTab)
        ))
