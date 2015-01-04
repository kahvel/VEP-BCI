__author__ = 'Anti'

from widgets import Textboxes
from frames import Frame, SameTabsNotebookTab


class TargetsTab(SameTabsNotebookTab.SameTabsNotebookTab):
    def __init__(self, row, column, **kwargs):
        SameTabsNotebookTab.SameTabsNotebookTab.__init__(self, "TargetsTab", row, column, **kwargs)
        self.addChildWidgets((
            TargetFrame(0, 0, command=kwargs["validate_freq"]),
            self.getDisableDeleteFrame(1, 0, delete_tab=kwargs["delete_tab"])
        ))


class TargetFrame(Frame.Frame):
    def __init__(self, row, column, **kwargs):
        Frame.Frame.__init__(self, "TargetFrame", row, column, **kwargs)
        validate_freq = lambda x: kwargs["validate_freq"](self.widgets_dict["Freq"], 0)
        increase = lambda: kwargs["validate_freq"](self.widgets_dict["Freq"], -1)
        decrease = lambda: kwargs["validate_freq"](self.widgets_dict["Freq"], 1)
        self.addChildWidgets((
            Textboxes.PlusMinusTextbox("Freq", 0, 0, increase, decrease, command=validate_freq, default_value=10.0),
            Textboxes.LabelTextbox("Delay", 0, 4, command=int, allow_zero=True),
            Textboxes.LabelTextbox("Width", 1, 0, command=int, default_value=150),
            Textboxes.LabelTextbox("Height", 1, 2, command=int, default_value=150),
            Textboxes.ColorTextbox("Color1", 1, 4, default_value="#ffffff"),
            Textboxes.LabelTextbox("x", 2, 0, command=int, allow_negative=True, allow_zero=True),
            Textboxes.LabelTextbox("y", 2, 2, command=int, allow_negative=True, allow_zero=True),
            Textboxes.ColorTextbox("Color2", 2, 4, default_value="#000000"),
        ))