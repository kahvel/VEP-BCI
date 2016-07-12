from gui.widgets.frames.notebooks import PlusNotebook, Notebook
from gui.widgets.frames.tabs import TestTab, WindowTab, RobotTab, EmotivTab, RecordTab
import constants as c


class MainNotebook(Notebook.Notebook):
    def __init__(self, parent, button_commands, row, column, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.MAIN_NOTEBOOK, row, column, **kwargs)
        target_notebook = PlusNotebook.TargetNotebook(self.widget, 0, 0, self.targetAdded, self.targetRemoved, self.targetDisabled, self.targetEnabled, self.getMonitorFreq)
        self.addChildWidgets((
            WindowTab.WindowTab(self.widget, 0, 0, self.monitorFreqChanged),
            target_notebook,
            PlusNotebook.ExtractionNotebook(self.widget, 0, 0, target_notebook.widgets_list),
            PlusNotebook.PlotNotebook(self.widget, 0, 0),
            TestTab.TestTab(self.widget, button_commands[c.TEST_TAB], 0, 0),
            RobotTab.RobotTab(self.widget, button_commands[c.ROBOT_TAB]),
            EmotivTab.EmotivTab(self.widget),
            RecordTab.RecordTab(self.widget, button_commands[c.RECORD_TAB]),
        ))

    def getMonitorFreq(self):
        return float(self.widgets_dict[c.WINDOW_TAB].widgets_dict[c.WINDOW_FREQ].getValue())

    def monitorFreqChanged(self):
        self.widgets_dict[c.TARGETS_TAB].changeFreq()
