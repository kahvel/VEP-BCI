from gui.widgets.frames.notebooks import SameTabsNotebook, Notebook
from gui.widgets.frames.tabs import TestTab, RecordTab
import constants as c


class TrainingNotebook(Notebook.Notebook):
    def __init__(self, parent, button_commands, row, column, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.MAIN_NOTEBOOK, row, column, **kwargs)
        self.addChildWidgets((
            SameTabsNotebook.ExtractionNotebook(self.widget, 0, 0, []),
            TestTab.TestTab(self.widget, button_commands[c.TEST_TAB], 0, 0),
            RecordTab.RecordTab(self.widget, button_commands[c.RECORD_TAB]),
        ))

    def getMonitorFreq(self):
        return float(self.widgets_dict[c.WINDOW_TAB].widgets_dict[c.WINDOW_FREQ].getValue())

    def monitorFreqChanged(self):
        self.widgets_dict[c.TARGETS_TAB].changeFreq()
