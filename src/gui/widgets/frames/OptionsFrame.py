from gui.widgets import Checkbutton, Textboxes, OptionMenu
from gui.widgets.frames import Frame

import constants as c


class OptionsFrameFrame(Frame.Frame):
    def getValue(self):
        return [widget.name for widget in self.widgets_list if widget.getValue() == 1]


class SensorsFrame(OptionsFrameFrame):
    def __init__(self, parent, row, column, **kwargs):
        OptionsFrameFrame.__init__(self, parent, c.SENSORS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Checkbutton.Checkbutton(self, c.SENSORS[0], 0, 0, pady=0, padx=0),
            Checkbutton.Checkbutton(self, c.SENSORS[1], 0, 1, pady=0, padx=0),
            Checkbutton.Checkbutton(self, c.SENSORS[2], 0, 2, pady=0, padx=0),
            Checkbutton.Checkbutton(self, c.SENSORS[3], 0, 3, pady=0, padx=0),
            Checkbutton.Checkbutton(self, c.SENSORS[4], 0, 4, pady=0, padx=0),
            Checkbutton.Checkbutton(self, c.SENSORS[5], 0, 5, pady=0, padx=0),
            Checkbutton.Checkbutton(self, c.SENSORS[6], 0, 6, pady=0, padx=0, default_value=1),
            Checkbutton.Checkbutton(self, c.SENSORS[7], 1, 0, pady=0, padx=0, default_value=1),
            Checkbutton.Checkbutton(self, c.SENSORS[8], 1, 1, pady=0, padx=0),
            Checkbutton.Checkbutton(self, c.SENSORS[9], 1, 2, pady=0, padx=0),
            Checkbutton.Checkbutton(self, c.SENSORS[10], 1, 3, pady=0, padx=0),
            Checkbutton.Checkbutton(self, c.SENSORS[11], 1, 4, pady=0, padx=0),
            Checkbutton.Checkbutton(self, c.SENSORS[12], 1, 5, pady=0, padx=0),
            Checkbutton.Checkbutton(self, c.SENSORS[13], 1, 6, pady=0, padx=0)
        ))


class OptionsFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.OPTIONS_FRAME, row, column, **kwargs)
        windows = c.WINDOW_FUNCTION_NAMES
        detrends = c.DETREND_NAMES
        filters = c.FILTER_NAMES
        interpolations = c.INTERPOLATE_NAMES
        self.addChildWidgets((
            OptionMenu.OptionMenu  (self, c.OPTIONS_DETREND,     0, 1, detrends, command=self.enableBreak),
            OptionMenu.OptionMenu  (self, c.OPTIONS_WINDOW,      0, 4, windows, command=self.enableWindow),
            OptionMenu.OptionMenu  (self, c.OPTIONS_INTERPOLATE, 1, 1, interpolations),
            OptionMenu.OptionMenu  (self, c.OPTIONS_FILTER,      1, 4, filters, command=self.enableFilter),
            Textboxes.LabelTextbox (self, c.OPTIONS_STEP,        2, 0, command=int,    default_value=32),
            Textboxes.LabelTextbox (self, c.OPTIONS_LENGTH,      2, 2, command=int,    default_value=512),
            Checkbutton.Checkbutton(self, c.OPTIONS_NORMALISE,   2, 4, columnspan=2),
            Textboxes.LabelTextbox (self, c.OPTIONS_BREAK,       3, 0, command=int,   allow_zero=True),
            Textboxes.LabelTextbox (self, c.OPTIONS_ARG,         3, 2, command=int,   allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_WINDOW]),
            Checkbutton.Checkbutton(self, c.OPTIONS_LOG10,       3, 4, columnspan=2),
            Textboxes.LabelTextbox (self, c.OPTIONS_FROM,        4, 0, command=float, allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER]),
            Textboxes.LabelTextbox (self, c.OPTIONS_TO,          4, 2, command=float, allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER]),
            Textboxes.LabelTextbox (self, c.OPTIONS_TAPS,        4, 4, command=int,   allow_zero=True, default_disability=True, default_disablers=[c.OPTIONS_FILTER])
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
