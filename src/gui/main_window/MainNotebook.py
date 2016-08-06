from gui_elements.widgets.frames.notebooks import Notebook
from gui.main_window.window_tab import WindowTab
from gui.main_window.extraction_tab import ExtractionNotebook
from gui.main_window.plot_tab import PlotNotebook
from gui.main_window.test_tab import TestTab
from gui.main_window.robot_tab import RobotTab
from gui.main_window.eeg_tab import EegTab
from gui.main_window.record_tab import RecordTab
import constants as c


class MainNotebook(Notebook.Notebook):
    def __init__(self, parent, row, column, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.MAIN_NOTEBOOK, row, column, **kwargs)
        self.addChildWidgets((
            WindowTab.WindowTab(self, 0, 0),
            ExtractionNotebook.ExtractionNotebook(self, 0, 0),
            PlotNotebook.PlotNotebook(self, 0, 0),
            TestTab.TestTab(self, 0, 0),
            RobotTab.RobotTab(self),
            EegTab.EegTab(self),
            RecordTab.RecordTab(self, 0, 0),
        ))
