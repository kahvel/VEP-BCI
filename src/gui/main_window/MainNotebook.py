from gui_elements.widgets.frames.notebooks import Notebook
from gui.main_window.targets_tab import TargetsTab
from gui.main_window.extraction_tab import ExtractionNotebook
from gui.main_window.plot_tab import PlotNotebook
from gui.main_window.test_tab import TestTab
from gui.main_window.robot_tab import RobotTab
from gui.main_window.classification_tab import ClassificationTab
from gui.main_window.record_tab import RecordTab
import constants as c


class MainNotebook(Notebook.Notebook):
    def __init__(self, parent, row, column, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.MAIN_NOTEBOOK, row, column, **kwargs)
        self.addChildWidgets((
            TargetsTab.TargetsTab(self, 0, 0),
            ExtractionNotebook.ExtractionNotebook(self, 0, 0),
            PlotNotebook.PlotNotebook(self, 0, 0),
            TestTab.TestTab(self, 0, 0),
            RobotTab.RobotTab(self),
            ClassificationTab.ClassificationTab(self),
            RecordTab.RecordTab(self, 0, 0),
        ))
