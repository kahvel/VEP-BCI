from gui_elements.widgets.frames.notebooks import Notebook
from gui.training_window import TrainingTab
from gui.main_window.record_tab import RecordTab
from gui.main_window.test_tab import TestTab
from gui.main_window.extraction_tab import ExtractionNotebook
import constants as c


class TrainingNotebook(Notebook.Notebook):
    def __init__(self, parent, row, column, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.MAIN_NOTEBOOK, row, column, **kwargs)
        self.addChildWidgets((
            ExtractionNotebook.ExtractionNotebook(self, 0, 0),
            TestTab.TestTab(self, 0, 0),
            RecordTab.RecordTab(self, 0, 0),
            TrainingTab.TrainingTab(self),
        ))
