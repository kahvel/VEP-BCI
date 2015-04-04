__author__ = 'Anti'

from widgets import Checkbutton, Buttons, Textboxes, OptionMenu
from frames import Frame, SameTabsNotebookTab
import constants as c


class ExtractionTab(SameTabsNotebookTab.SameTabsNotebookTab):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebookTab.SameTabsNotebookTab.__init__(self, parent, c.EXTRACTION_TAB_TAB, row, column, **kwargs)
        self.addChildWidgets((
            SensorsFrame(self.widget, 0, 0),
            ExtractionTabButtonFrame(self.widget, 1, 0),
            OptionsFrame(self.widget, 2, 0),
            self.getDisableDeleteFrame(3, 0, delete_tab=kwargs["delete_tab"])
        ))


class PlotTab(SameTabsNotebookTab.SameTabsNotebookTab):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebookTab.SameTabsNotebookTab.__init__(self, parent, c.PLOT_TAB_TAB, row, column, **kwargs)
        self.addChildWidgets((
            SensorsFrame(self.widget, 0, 0),
            PlotTabButtonFrame(self.widget, 1, 0),
            OptionsFrame(self.widget, 2, 0),
            self.getDisableDeleteFrame(3, 0, delete_tab=kwargs["delete_tab"])
        ))


class SensorsFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.SENSORS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Checkbutton.Checkbutton(self.widget, c.SENSORS[0], 0, 0, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[1], 0, 1, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[2], 0, 2, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[3], 0, 3, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[4], 0, 4, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[5], 0, 5, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[6], 0, 6, pady=0, padx=0, default_value=1),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[7], 1, 0, pady=0, padx=0, default_value=1),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[8], 1, 1, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[9], 1, 2, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[10], 1, 3, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[11], 1, 4, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[12], 1, 5, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, c.SENSORS[13], 1, 6, pady=0, padx=0)
        ))


class OptionsFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.OPTIONS_FRAME, row, column, **kwargs)
        windows = (c.WINDOW_NONE, c.WINDOW_HANNING, c.WINDOW_HAMMING, c.WINDOW_BLACKMAN, c.WINDOW_KAISER, c.WINDOW_BARTLETT)
        self.addChildWidgets((
            Checkbutton.Checkbutton(self.widget, c.OPTIONS_NORMALISE, 0, 0,                      columnspan=2),
            Checkbutton.Checkbutton(self.widget, c.OPTIONS_DETREND,   0, 2,                      columnspan=2),
            Checkbutton.Checkbutton(self.widget, c.OPTIONS_FILTER,    0, 4, command=self.disableFilter,      columnspan=2),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_STEP,      1, 0, command=int,    default_value=32),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_LENGTH,    1, 2, command=int,    default_value=512),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_FROM,      3, 0, command=float, allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER]),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_TO,        3, 2, command=float, allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER]),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_TAPS,      3, 4, command=int,   allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER]),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_ARG,      4, 2, command=int,   allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_WINDOW]),
            OptionMenu.OptionMenu  (self.widget, c.OPTIONS_WINDOW,    4, 0, command=self.disableWindow, values=windows),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_BREAK,     4, 4, command=int,   allow_zero=True)
        ))

    def disableFilter(self):
        self.conditionalDisabling(
            self.widgets_dict[c.OPTIONS_FILTER],
            1,
            (
                self.widgets_dict[c.OPTIONS_FROM],
                self.widgets_dict[c.OPTIONS_TO],
                self.widgets_dict[c.OPTIONS_TAPS]
            )
        )

    def disableWindow(self):
        self.conditionalDisabling(
            self.widgets_dict[c.OPTIONS_WINDOW],
            c.WINDOW_KAISER,
            (
                self.widgets_dict[c.OPTIONS_ARG],
            )
        )


class ExtractionTabButtonFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent,c.EXTRACTION_TAB_BUTTON_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton(self.widget, c.PSDA,     0, 0),
            Buttons.SunkenButton(self.widget, c.SUM_PSDA, 0, 1),
            Buttons.SunkenButton(self.widget, c.CCA,      0, 2),
            Buttons.SunkenButton(self.widget, c.BOTH,     0, 3),
            Buttons.SunkenButton(self.widget, c.SUM_BOTH, 0, 4),
        ))


class PlotTabButtonFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.PLOT_TAB_BUTTON_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton(self.widget, c.SIGNAL,         0, 0),
            Buttons.SunkenButton(self.widget, c.SUM_SIGNAL,     0, 1),
            Buttons.SunkenButton(self.widget, c.AVG_SIGNAL,     0, 2),
            Buttons.SunkenButton(self.widget, c.SUM_AVG_SIGNAL, 0, 3),
            Buttons.SunkenButton(self.widget, c.POWER,          1, 0),
            Buttons.SunkenButton(self.widget, c.SUM_POWER,      1, 1),
            Buttons.SunkenButton(self.widget, c.AVG_POWER,      1, 2),
            Buttons.SunkenButton(self.widget, c.SUM_AVG_POWER,  1, 3)
        ))