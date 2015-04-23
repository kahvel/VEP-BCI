__author__ = 'Anti'

from frames import Frame
import constants as c
from widgets import Checkbutton, Textboxes, OptionMenu


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

    def enableFilter(self):
        self.enableFrom()
        self.enableTo()
        self.enableTaps()

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


class PsdaOptionsFrame(OptionsFrame):
    def __init__(self, parent, row, column, **kwargs):
        OptionsFrame.__init__(self, parent, row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_STEP,      0, 0, command=int,    default_value=32),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_LENGTH,    0, 2, command=int,    default_value=512),
            Checkbutton.Checkbutton(self.widget, c.OPTIONS_NORMALISE, 0, 4,                      columnspan=2),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_BREAK,     1, 0, command=int,   allow_zero=True),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_ARG,       1, 2, command=int,   allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_WINDOW]),
            OptionMenu.OptionMenu  (self.widget, c.OPTIONS_DETREND,   2, 1, values=c.DETREND_NAMES),
            OptionMenu.OptionMenu  (self.widget, c.OPTIONS_WINDOW,    2, 4, command=self.enableWindow, values=c.WINDOW_FUNCTION_NAMES),
            OptionMenu.OptionMenu  (self.widget, c.OPTIONS_INTERPOLATE, 3, 1, values=c.INTERPOLATE_NAMES),
            OptionMenu.OptionMenu  (self.widget, c.OPTIONS_FILTER,    3, 4, values=c.FILTER_NAMES, command=self.enableFilter),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_FROM,      4, 0, command=float, allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER]),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_TO,        4, 2, command=float, allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER]),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_TAPS,      4, 4, command=int,   allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER])
        ))


class CcaOptionsFrame(OptionsFrame):
    def __init__(self, parent, row, column, **kwargs):
        OptionsFrame.__init__(self, parent, row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_STEP,      0, 0, command=int,    default_value=32),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_LENGTH,    0, 2, command=int,    default_value=512),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_BREAK,     1, 0, command=int,   allow_zero=True),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_ARG,       1, 2, command=int,   allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_WINDOW]),
            OptionMenu.OptionMenu  (self.widget, c.OPTIONS_DETREND,   2, 1, values=c.DETREND_NAMES),
            OptionMenu.OptionMenu  (self.widget, c.OPTIONS_WINDOW,    2, 4, command=self.enableWindow, values=c.WINDOW_FUNCTION_NAMES),
            OptionMenu.OptionMenu  (self.widget, c.OPTIONS_FILTER,    3, 4, values=c.FILTER_NAMES, command=self.enableFilter),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_FROM,      4, 0, command=float, allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER]),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_TO,        4, 2, command=float, allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER]),
            Textboxes.LabelTextbox (self.widget, c.OPTIONS_TAPS,      4, 4, command=int,   allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER])
        ))
