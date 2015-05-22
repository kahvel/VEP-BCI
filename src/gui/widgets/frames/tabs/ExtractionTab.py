from gui.widgets.frames.notebooks import ExtractionMethods
from gui.widgets.frames.tabs import DisableDeleteNotebookTab

__author__ = 'Anti'

import constants as c


class ExtractionTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.EXTRACTION_TAB, **kwargs)
        self.addChildWidgets((
            # SameTabsNotebook.ExtractionNotebook(self.widget, 0, 0, **kwargs),
            ExtractionMethods.ExtractionMethods(self.widget, 0, 0, **kwargs),
            self.getDisableDeleteFrame(1, 0, **kwargs)
        ))
