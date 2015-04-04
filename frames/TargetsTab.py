__author__ = 'Anti'

from widgets import Textboxes
from frames import Frame, SameTabsNotebookTab
import constants as c


class TargetsTab(SameTabsNotebookTab.SameTabsNotebookTab):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebookTab.SameTabsNotebookTab.__init__(self, parent, c.TARGETS_TAB_TAB, row, column, **kwargs)
        self.addChildWidgets((
            TargetFrame(self.widget, 0, 0, validate_freq=kwargs["validate_freq"]),
            self.getDisableDeleteFrame(1, 0, delete_tab=kwargs["delete_tab"])
        ))


class TargetFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.TARGET_FRAME, row, column, **kwargs)
        validate_freq = lambda: kwargs["validate_freq"](self.widgets_dict[c.PLUS_MINUS_TEXTOX_FRAME].widgets_dict[c.TARGET_FREQ], 0)
        increase      = lambda: kwargs["validate_freq"](self.widgets_dict[c.PLUS_MINUS_TEXTOX_FRAME].widgets_dict[c.TARGET_FREQ], -1)
        decrease      = lambda: kwargs["validate_freq"](self.widgets_dict[c.PLUS_MINUS_TEXTOX_FRAME].widgets_dict[c.TARGET_FREQ], 1)
        self.addChildWidgets((
            Textboxes.PlusMinusTextboxFrame(self.widget, c.TARGET_FREQ,   0, 0, increase, decrease, command=validate_freq, default_value=10.0),
            Textboxes.LabelTextbox         (self.widget, c.TARGET_DELAY,  0, 4, command=int, allow_zero=True),
            Textboxes.LabelTextbox         (self.widget, c.TARGET_WIDTH,  1, 0, command=int, default_value=150),
            Textboxes.LabelTextbox         (self.widget, c.TARGET_HEIGHT, 1, 2, command=int, default_value=150),
            Textboxes.ColorTextboxFrame    (self.widget, c.TARGET_COLOR1, 1, 4, default_value="#ffffff"),
            Textboxes.LabelTextbox         (self.widget, c.TARGET_X,      2, 0, command=int, allow_negative=True, allow_zero=True),
            Textboxes.LabelTextbox         (self.widget, c.TARGET_Y,      2, 2, command=int, allow_negative=True, allow_zero=True),
            Textboxes.ColorTextboxFrame    (self.widget, c.TARGET_COLOR2, 2, 4, default_value="#000000"),
        ))