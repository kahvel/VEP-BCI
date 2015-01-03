__author__ = 'Anti'

from widgets import Textboxes, Frame, Buttons
import SameTabsNotebookTab


class PlusMinusFrame(Frame.Frame):
    def __init__(self, row, column, columnspan, padx, pady, validate_freq):
        Frame.Frame.__init__(self, "PlusMinusTab", row, column, columnspan, padx, pady)
        self.setChildWidgets((
            Buttons.Button(" -", 0, 0, lambda: validate_freq(1),  command_on_load=False),
            Buttons.Button("+",  0, 1, lambda: validate_freq(-1), command_on_load=False)
        ))


class TargetsTab(SameTabsNotebookTab.SameTabsNotebookTab):
    def __init__(self, row, column, columnspan, padx, pady, delete_tab, validate_freq_arg):
        SameTabsNotebookTab.SameTabsNotebookTab.__init__(self, "TargetsTab", row, column, columnspan, padx, pady, delete_tab)
        validate_freq = lambda d: validate_freq_arg(self.widgets_dict["Freq"], d)
        self.setChildWidgets((
            Textboxes.LabelTextbox("Freq", 0, 0, lambda x: validate_freq(0), False, False, default_value=10.0),
            PlusMinusFrame(0, 2, 1, 0, 0, validate_freq),
            Textboxes.LabelTextbox("Delay", 0, 4, int, False, True),
            Textboxes.LabelTextbox("Width", 1, 0, int, False, False, default_value=150),
            Textboxes.LabelTextbox("Height", 1, 2, int, False, False, default_value=150),
            Textboxes.ColorTextbox("Color1", 1, 4, default_value="#ffffff"),
            Textboxes.LabelTextbox("x", 2, 0, int, True, True),
            Textboxes.LabelTextbox("y", 2, 2, int, True, True),
            Textboxes.ColorTextbox("Color2", 2, 4, default_value="#000000"),
            self.getDisableDeleteFrame(3, 0, 2, 0, 0)
        ))