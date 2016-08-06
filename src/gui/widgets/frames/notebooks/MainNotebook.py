from gui.widgets.frames.notebooks import PlusNotebook, Notebook
from gui.widgets.frames.tabs import TestTab, WindowTab, RobotTab, EmotivTab
from gui.widgets.frames import RecordFrame
import constants as c


class MainNotebook(Notebook.Notebook):
    def __init__(self, parent, row, column, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.MAIN_NOTEBOOK, row, column, **kwargs)
        self.addChildWidgets((
            WindowTab.WindowTab(self, 0, 0),
            PlusNotebook.ExtractionNotebook(self, 0, 0),
            PlusNotebook.PlotNotebook(self, 0, 0),
            TestTab.TestTab(self, 0, 0),
            RobotTab.RobotTab(self),
            EmotivTab.EmotivTab(self),
            RecordFrame.RecordFrame(self, 0, 0),
        ))
