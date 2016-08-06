from gui_elements.widgets.frames.notebooks import PlusNotebook
import ExtractionNotebookTab
import constants as c


class ExtractionNotebook(PlusNotebook.PlusNotebook):
    def __init__(self, parent, row, column, **kwargs):
        PlusNotebook.PlusNotebook.__init__(self, parent, c.EXTRACTION_NOTEBOOK, row, column, **kwargs)

    def newTab(self, deleteTab):
        return ExtractionNotebookTab.ExtractionNotebookTab(self, deleteTab)
