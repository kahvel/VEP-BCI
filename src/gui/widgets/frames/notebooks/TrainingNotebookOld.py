from gui.widgets.frames.notebooks import Notebook
from gui.widgets.frames.tabs import DisableDeleteNotebookTab
from gui.widgets import Textboxes

import constants as c


class TrainingNotebook(Notebook.Notebook):
    def __init__(self, parent, row, column, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.TRAINING_NOTEBOOK, row, column, **kwargs)
        self.tab_count = 0

    def addNormalEegTab(self, deleteTab):
        self.tab_count += 1
        self.widget.add(NormalEegTab(self.widget, deleteTab).widget, text=self.tab_count)

    def addNeutralEegTab(self, deleteTab):
        self.tab_count += 1
        self.widget.add(NeutralEegTab(self.widget, deleteTab).widget, text=self.tab_count)

    def deleteTab(self):
        self.tab_count -= 1
        current = self.getCurrentTab()
        del self.widgets_list[current]
        self.widget.forget(current)
        return current

    def getCurrentTab(self):
        return self.widget.index("current")


class NormalEegTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, deleteTab, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.NORMAL_EEG_TAB, **kwargs)
        self.addChildWidgets((
            Textboxes.LabelTextbox(self.widget, c.RECORDING_LENGTH, 0, 0, default_disablers=c.NORMAL_EEG_TAB, default_disability=True),
            self.getDisableDeleteFrame(1, 0, deleteTab),
        ))


class NeutralEegTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, deleteTab, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.NORMAL_EEG_TAB, **kwargs)
        self.addChildWidgets((
            Textboxes.LabelTextbox(self.widget, c.RECORDING_LENGTH, 0, 0, default_disablers=c.NORMAL_EEG_TAB, default_disability=True),
            self.getDisableDeleteFrame(1, 0, deleteTab),
        ))
