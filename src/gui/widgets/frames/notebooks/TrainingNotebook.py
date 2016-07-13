from gui.widgets.frames.notebooks import PlusNotebook, Notebook
from gui.widgets.frames.tabs import TestTab, RecordTab, TrainingTab
import constants as c


class TrainingNotebook(Notebook.Notebook):
    def __init__(self, parent, button_commands, row, column, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.MAIN_NOTEBOOK, row, column, **kwargs)
        self.addChildWidgets((
            PlusNotebook.ExtractionNotebook(self.widget, 0, 0, []),
            TestTab.TestTab(self.widget, button_commands[c.TEST_TAB], 0, 0),
            RecordTab.RecordTab(self.widget, button_commands[c.RECORD_TAB]),
            TrainingTab.TrainingTab(self.widget),
        ))
