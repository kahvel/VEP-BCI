__author__ = 'Anti'

from widgets import Textboxes
from frames import Frame, SameTabsNotebookTab


class TargetsTab(SameTabsNotebookTab.SameTabsNotebookTab):
    def __init__(self, row, column, columnspan, padx, pady, delete_tab, validate_freq_arg):
        SameTabsNotebookTab.SameTabsNotebookTab.__init__(self, "TargetsTab", row, column, columnspan, padx, pady, delete_tab)
        self.addChildWidgets((
            TargetFrame(0, 0, 1, 0, 0, validate_freq_arg),
            self.getDisableDeleteFrame(1, 0, 1, 0, 0)
        ))


class TargetFrame(Frame.Frame):
    def __init__(self, row, column, columnspan, padx, pady, validate_freq_arg):
        Frame.Frame.__init__(self, "TargetFrame", row, column, columnspan, padx, pady)
        validate_freq = lambda x: validate_freq_arg(self.widgets_dict["Freq"], 0)
        increase = lambda: validate_freq_arg(self.widgets_dict["Freq"], -1)
        decrease = lambda: validate_freq_arg(self.widgets_dict["Freq"], 1)
        self.addChildWidgets((
            Textboxes.PlusMinusTextbox("Freq", 0, 0, increase, decrease, validate_freq, False, False, default_value=10.0),
            Textboxes.LabelTextbox("Delay", 0, 4, int, False, True),
            Textboxes.LabelTextbox("Width", 1, 0, int, False, False, default_value=150),
            Textboxes.LabelTextbox("Height", 1, 2, int, False, False, default_value=150),
            Textboxes.ColorTextbox("Color1", 1, 4, default_value="#ffffff"),
            Textboxes.LabelTextbox("x", 2, 0, int, True, True),
            Textboxes.LabelTextbox("y", 2, 2, int, True, True),
            Textboxes.ColorTextbox("Color2", 2, 4, default_value="#000000"),
        ))