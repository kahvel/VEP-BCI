from gui.widgets.frames.notebooks import SameTabsNotebook, Notebook
from gui.widgets.frames.tabs import TestTab, WindowTab, RobotTab, EmotivTab, TrainingTab
import constants as c


class MainNotebook(Notebook.Notebook):
    def __init__(self, parent, buttons, row, column, **kwargs):
        test_tab_buttons, robot_buttons, training_tab_buttons = buttons
        Notebook.Notebook.__init__(self, parent, c.MAIN_NOTEBOOK, row, column, **kwargs)
        self.addChildWidgets((
            WindowTab.WindowTab(self.widget, 0, 0, self.monitorFreqChanged),
            SameTabsNotebook.TargetNotebook(self.widget, 0, 0, self.targetAdded, self.targetRemoved, self.targetDisabled, self.targetEnabled, self.getMonitorFreq),
            SameTabsNotebook.ExtractionNotebook(self.widget, 0, 0),
            SameTabsNotebook.PlotNotebook(self.widget, 0, 0),
            TestTab.TestTab(self.widget, test_tab_buttons, 0, 0),
            RobotTab.RobotTab(self.widget, robot_buttons),
            EmotivTab.EmotivTab(self.widget),
            TrainingTab.TrainingTab(self.widget, training_tab_buttons)
        ))

    def getMonitorFreq(self):
        return float(self.widgets_dict[c.WINDOW_TAB].widgets_dict[c.WINDOW_FREQ].getValue())

    def monitorFreqChanged(self):
        self.widgets_dict[c.TARGETS_TAB].changeFreq()
