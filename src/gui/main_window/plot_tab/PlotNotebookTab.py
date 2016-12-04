from gui_elements.widgets.frames import OptionsFrame
from gui_elements.widgets import Buttons
import gui_elements.widgets.frames.tabs.DisableDeleteNotebookTab

import constants as c


class PlotNotebookTab(gui_elements.widgets.frames.tabs.DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, deleteTab, **kwargs):
        gui_elements.widgets.frames.tabs.DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.PLOT_NOTEBOOK_TAB, **kwargs)
        self.addChildWidgets((
            OptionsFrame.SensorsFrame(self, 0, 0),
            PlotTabButtonFrame(self, 1, 0),
            OptionsFrame.OptionsFrame(self, 2, 0),
            self.getDisableDeleteFrame(3, 0, deleteTab)
        ))


class PlotTabButtonFrame(OptionsFrame.OptionsFrameFrame):
    def __init__(self, parent, row, column, **kwargs):
        OptionsFrame.OptionsFrameFrame.__init__(self, parent, c.METHODS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton(self, c.SIGNAL,         0, 0, default_value=1),
            Buttons.SunkenButton(self, c.SUM_SIGNAL,     0, 1),
            Buttons.SunkenButton(self, c.AVG_SIGNAL,     0, 2),
            Buttons.SunkenButton(self, c.SUM_AVG_SIGNAL, 0, 3),
            Buttons.SunkenButton(self, c.POWER,          1, 0),
            Buttons.SunkenButton(self, c.SUM_POWER,      1, 1),
            Buttons.SunkenButton(self, c.AVG_POWER,      1, 2),
            Buttons.SunkenButton(self, c.SUM_AVG_POWER,  1, 3)
        ))
