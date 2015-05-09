__author__ = 'Anti'

from widgets import Checkbutton, Buttons, Textboxes, OptionMenu
from frames import Frame, DisableDeleteNotebookTab
import constants as c


class ExtractionTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, row, column, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.EXTRACTION_TAB_TAB, **kwargs)
        self.addChildWidgets((
            SensorsFrame(self.widget, 0, 0),
            ExtractionTabButtonFrame(self.widget, 1, 0),
            OptionsFrame(self.widget, 2, 0),
            self.getDisableDeleteFrame(3, 0, delete_tab=kwargs["delete_tab"])
        ))


class PlotTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, row, column, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.PLOT_TAB_TAB, **kwargs)
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
        windows = c.WINDOW_FUNCTION_NAMES
        detrends = c.DETREND_NAMES
        filters = c.FILTER_NAMES
        interpolations = c.INTERPOLATE_NAMES
        self.addChildWidgets((
            OptionMenu.OptionMenu  (self.widget, c.OPTIONS_DETREND,     0, 1, values=detrends, command=self.enableBreak),
            OptionMenu.OptionMenu  (self.widget, c.OPTIONS_WINDOW,      0, 4, command=self.enableWindow, values=windows),
            OptionMenu.OptionMenu  (self.widget, c.OPTIONS_INTERPOLATE, 1, 1, values=interpolations),
            OptionMenu.OptionMenu  (self.widget, c.OPTIONS_FILTER,      1, 4, values=filters, command=self.enableFilter),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_STEP,        2, 0, command=int,    default_value=32),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_LENGTH,      2, 2, command=int,    default_value=512),
            Checkbutton.Checkbutton(self.widget, c.OPTIONS_NORMALISE,   2, 4, columnspan=2),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_BREAK,       3, 0, command=int,   allow_zero=True),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_ARG,         3, 2, command=int,   allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_WINDOW]),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_FROM,        4, 0, command=float, allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER]),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_TO,          4, 2, command=float, allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER]),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_TAPS,        4, 4, command=int,   allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER])
        ))

    def enableFilter(self):
        self.enableFrom()
        self.enableTo()
        self.enableTaps()

    def enableBreak(self):
        self.conditionalDisabling(
            self.widgets_dict[c.OPTIONS_DETREND],
            (c.CONSTANT_DETREND, c.LINEAR_DETREND),
            (self.widgets_dict[c.OPTIONS_BREAK],)
        )

    def enableTaps(self):
        self.conditionalDisabling(
            self.widgets_dict[c.OPTIONS_FILTER],
            (c.LOWPASS_FILTER, c.HIGHPASS_FILTER, c.BANDPASS_FILTER),
            (self.widgets_dict[c.OPTIONS_TAPS],)
        )

    def enableFrom(self):
        self.conditionalDisabling(
            self.widgets_dict[c.OPTIONS_FILTER],
            (c.HIGHPASS_FILTER, c.BANDPASS_FILTER),
            (self.widgets_dict[c.OPTIONS_FROM], self.widgets_dict[c.OPTIONS_TAPS])
        )

    def enableTo(self):
        self.conditionalDisabling(
            self.widgets_dict[c.OPTIONS_FILTER],
            (c.LOWPASS_FILTER, c.BANDPASS_FILTER),
            (self.widgets_dict[c.OPTIONS_TO], self.widgets_dict[c.OPTIONS_TAPS])
        )

    def enableWindow(self):
        self.conditionalDisabling(
            self.widgets_dict[c.OPTIONS_WINDOW],
            (c.WINDOW_KAISER,),
            (self.widgets_dict[c.OPTIONS_ARG],)
        )


class ExtractionTabButtonFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent,c.EXTRACTION_TAB_BUTTON_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton(self.widget, c.PSDA,     0, 0),
            Buttons.SunkenButton(self.widget, c.SUM_PSDA, 0, 1),
            Buttons.SunkenButton(self.widget, c.CCA,      0, 2),
        ))


class PlotTabButtonFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.PLOT_TAB_BUTTON_FRAME, row, column, **kwargs)
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