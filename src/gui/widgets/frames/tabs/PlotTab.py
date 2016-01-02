from gui.widgets.frames import OptionsFrame
from gui.widgets import Buttons
import DisableDeleteNotebookTab

import constants as c


class PlotTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, deleteTab, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.PLOT_TAB_TAB, **kwargs)
        self.addChildWidgets((
            OptionsFrame.SensorsFrame(self.widget, 0, 0),
            PlotTabButtonFrame(self.widget, 1, 0),
            OptionsFrame.OptionsFrame(self.widget, 2, 0),
            self.getDisableDeleteFrame(3, 0, deleteTab)
        ))


class PlotTabButtonFrame(OptionsFrame.OptionsFrameFrame):
    def __init__(self, parent, row, column, **kwargs):
        OptionsFrame.OptionsFrameFrame.__init__(self, parent, c.METHODS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton(self.widget, c.SIGNAL,         0, 0, default_value=1),
            Buttons.SunkenButton(self.widget, c.SUM_SIGNAL,     0, 1),
            Buttons.SunkenButton(self.widget, c.AVG_SIGNAL,     0, 2),
            Buttons.SunkenButton(self.widget, c.SUM_AVG_SIGNAL, 0, 3),
            Buttons.SunkenButton(self.widget, c.POWER,          1, 0),
            Buttons.SunkenButton(self.widget, c.SUM_POWER,      1, 1),
            Buttons.SunkenButton(self.widget, c.AVG_POWER,      1, 2),
            Buttons.SunkenButton(self.widget, c.SUM_AVG_POWER,  1, 3)
        ))
