__author__ = 'Anti'

from widgets import Textboxes
from frames import Frame, SameTabsNotebookTab


class TargetsTab(SameTabsNotebookTab.SameTabsNotebookTab):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebookTab.SameTabsNotebookTab.__init__(self, parent, "TargetsTab", row, column, **kwargs)
        self.addChildWidgets((
            TargetFrame(self.widget, 0, 0, validate_freq=kwargs["validate_freq"]),
            self.getDisableDeleteFrame(1, 0, delete_tab=kwargs["delete_tab"])
        ))


class TargetFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, "TargetFrame", row, column, **kwargs)
        validate_freq = lambda: kwargs["validate_freq"](self.widgets_dict["PlusMinusTextboxFrame"].widgets_dict["Freq"], 0)
        increase = lambda: kwargs["validate_freq"](self.widgets_dict["PlusMinusTextboxFrame"].widgets_dict["Freq"], -1)
        decrease = lambda: kwargs["validate_freq"](self.widgets_dict["PlusMinusTextboxFrame"].widgets_dict["Freq"], 1)
        self.addChildWidgets((
            Textboxes.PlusMinusTextboxFrame(self.widget, "Freq", 0, 0, increase, decrease, command=validate_freq, default_value=10.0),
            Textboxes.LabelTextbox(self.widget, "Delay", 0, 4, command=int, allow_zero=True),
            Textboxes.LabelTextbox(self.widget, "Width", 1, 0, command=int, default_value=150),
            Textboxes.LabelTextbox(self.widget, "Height", 1, 2, command=int, default_value=150),
            Textboxes.ColorTextboxFrame(self.widget, "Color1", 1, 4, default_value="#ffffff"),
            Textboxes.LabelTextbox(self.widget, "x", 2, 0, command=int, allow_negative=True, allow_zero=True),
            Textboxes.LabelTextbox(self.widget, "y", 2, 2, command=int, allow_negative=True, allow_zero=True),
            Textboxes.ColorTextboxFrame(self.widget, "Color2", 2, 4, default_value="#000000"),
        ))