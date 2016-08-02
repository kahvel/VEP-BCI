from gui.widgets.frames.notebooks import PlusNotebook, Notebook
from gui.widgets.frames.tabs import TestTab, WindowTab, RobotTab, EmotivTab, RecordTab
import constants as c


class MainNotebook(Notebook.Notebook):
    def __init__(self, parent, row, column, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.MAIN_NOTEBOOK, row, column, **kwargs)
        target_notebook = PlusNotebook.TargetNotebook(self, 0, 0, self.getMonitorFreq)
        self.addChildWidgets((
            WindowTab.WindowTab(self, 0, 0, self.monitorFreqChanged),
            target_notebook,
            PlusNotebook.ExtractionNotebook(self, 0, 0, target_notebook.widgets_list),
            PlusNotebook.PlotNotebook(self, 0, 0),
            TestTab.TestTab(self, 0, 0),
            RobotTab.RobotTab(self),
            EmotivTab.EmotivTab(self),
            RecordTab.RecordTab(self),
        ))

    def getMonitorFreq(self):
        return float(self.widgets_dict[c.WINDOW_TAB].widgets_dict[c.WINDOW_FREQ].getValue())

    def monitorFreqChanged(self):
        self.widgets_dict[c.TARGETS_TAB].changeFreq()
