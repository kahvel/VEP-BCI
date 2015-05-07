__author__ = 'Anti'

from frames import WindowTab, TestTab, RecordTab
from notebooks import SameTabsNotebook, Notebook
import constants as c


class MainNotebook(Notebook.Notebook):
    def __init__(self, parent, buttons, row, column, **kwargs):
        test_tab_buttons = buttons
        Notebook.Notebook.__init__(self, parent, c.MAIN_NOTEBOOK, row, column, **kwargs)
        self.test_tab = TestTab.TestTab(self.widget, test_tab_buttons, 0, 0)
        self.addChildWidgets((
            WindowTab.WindowTab(self.widget, 0, 0, self.monitorFreqChanged),
            SameTabsNotebook.TargetNotebook(self.widget, 0, 0, self.targetAdded, self.targetRemoved, self.getMonitorFreq),
            SameTabsNotebook.ExtractionNotebook(self.widget, 0, 0),
            SameTabsNotebook.PlotNotebook(self.widget, 0, 0),
            self.test_tab,
            RecordTab.RecordTab(self.widget, 0, 0)
        ))

    def getMonitorFreq(self):
        return float(self.widgets_dict[c.WINDOW_TAB].widgets_dict[c.WINDOW_FREQ].getValue())

    def monitorFreqChanged(self):
        self.widgets_dict[c.TARGETS_TAB].changeFreq()

    def targetAdded(self):
        self.test_tab.targetAdded()

    def targetRemoved(self, deleted_tab):
        self.test_tab.targetRemoved(deleted_tab)
