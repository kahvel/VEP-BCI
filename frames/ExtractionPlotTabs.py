__author__ = 'Anti'

from widgets import Checkbutton, Buttons, Textboxes, OptionMenu
from frames import Frame, SameTabsNotebookTab


class ExtractionTab(SameTabsNotebookTab.SameTabsNotebookTab):
    def __init__(self, row, column, **kwargs):
        SameTabsNotebookTab.SameTabsNotebookTab.__init__(self, "ExtractionTab", row, column, **kwargs)
        self.addChildWidgets((
            SensorsFrame(0, 0),
            ExtractionTabButtonFrame(1, 0),
            OptionsFrame(2, 0),
            self.getDisableDeleteFrame(3, 0, delete_tab=kwargs["delete_tab"])
        ))


class PlotTab(SameTabsNotebookTab.SameTabsNotebookTab):
    def __init__(self, row, column, **kwargs):
        SameTabsNotebookTab.SameTabsNotebookTab.__init__(self, "PlotTab", row, column, **kwargs)
        self.addChildWidgets((
            SensorsFrame(0, 0),
            PlotTabButtonFrame(1, 0),
            OptionsFrame(2, 0),
            self.getDisableDeleteFrame(3, 0, delete_tab=kwargs["delete_tab"])
        ))


class SensorsFrame(Frame.Frame):
    def __init__(self, row, column, **kwargs):
        Frame.Frame.__init__(self, "SensorsFrame", row, column, **kwargs)
        self.addChildWidgets((
            Checkbutton.Checkbutton("AF3", 0, 0, pady=0, padx=0),
            Checkbutton.Checkbutton("F7",  0, 1, pady=0, padx=0),
            Checkbutton.Checkbutton("F3",  0, 2, pady=0, padx=0),
            Checkbutton.Checkbutton("FC5", 0, 3, pady=0, padx=0),
            Checkbutton.Checkbutton("T7",  0, 4, pady=0, padx=0),
            Checkbutton.Checkbutton("P7",  0, 5, pady=0, padx=0),
            Checkbutton.Checkbutton("O1",  0, 6, pady=0, padx=0, default_value=1),
            Checkbutton.Checkbutton("O2",  1, 0, pady=0, padx=0, default_value=1),
            Checkbutton.Checkbutton("P8",  1, 1, pady=0, padx=0),
            Checkbutton.Checkbutton("T8",  1, 2, pady=0, padx=0),
            Checkbutton.Checkbutton("FC6", 1, 3, pady=0, padx=0),
            Checkbutton.Checkbutton("F4",  1, 4, pady=0, padx=0),
            Checkbutton.Checkbutton("F8",  1, 5, pady=0, padx=0),
            Checkbutton.Checkbutton("AF4", 1, 6, pady=0, padx=0)
        ))


class OptionsFrame(Frame.Frame):
    def __init__(self, row, column, **kwargs):
        Frame.Frame.__init__(self, "OptionsFrame", row, column, **kwargs)
        windows = ("None", "Hanning", "Hamming", "Blackman", "Kaiser", "Bartlett")
        disable_window = lambda: self.conditionalDisabling(
            self.widgets_dict["Window"], "Kaiser", (
                self.widgets_dict["Beta"],
            )
        )
        disable_filter = lambda: self.conditionalDisabling(
            self.widgets_dict["Filter"], 1, (
                self.widgets_dict["From"],
                self.widgets_dict["To"],
                self.widgets_dict["Taps"]
            )
        )
        self.addChildWidgets((
            Checkbutton.Checkbutton("Normalise", 0, 0,                      columnspan=2),
            Checkbutton.Checkbutton("Detrend",   0, 2,                      columnspan=2),
            Checkbutton.Checkbutton("Filter",    0, 4, command=disable_filter,      columnspan=2),
            Textboxes.LabelTextbox ("Step",      1, 0, command=int,    default_value=32),
            Textboxes.LabelTextbox ("Length",    1, 2, command=int,    default_value=512),
            Textboxes.LabelTextbox ("From",      3, 0, command=float, allow_zero=True, default_disability=True, default_disablers=["Filter"]),
            Textboxes.LabelTextbox ("To",        3, 2, command=float, allow_zero=True, default_disability=True, default_disablers=["Filter"]),
            Textboxes.LabelTextbox ("Taps",      3, 4, command=int,   allow_zero=True, default_disability=True, default_disablers=["Filter"]),
            Textboxes.LabelTextbox ("Beta",      4, 2, command=int,   allow_zero=True, default_disability=True, default_disablers=["Window"]),
            OptionMenu.OptionMenu  ("Window",    4, 0, command=disable_window, values=windows),
            Textboxes.LabelTextbox ("Break",     4, 4, command=int,   allow_zero=True)
        ))


class ExtractionTabButtonFrame(Frame.Frame):
    def __init__(self, row, column, **kwargs):
        Frame.Frame.__init__(self, "ExtractionTabButtonFrame", row, column, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton("PSDA",     0, 0),
            Buttons.SunkenButton("Sum PSDA", 0, 1),
            Buttons.SunkenButton("CCA",      0, 2),
            Buttons.SunkenButton("Both",     0, 3),
            Buttons.SunkenButton("Sum Both", 0, 4),
        ))


class PlotTabButtonFrame(Frame.Frame):
    def __init__(self, row, column, **kwargs):
        Frame.Frame.__init__(self, "PlotTabButtonFrame", row, column, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton("Signal",         0, 0),
            Buttons.SunkenButton("Sum signal",     0, 1),
            Buttons.SunkenButton("Avg signal",     0, 2),
            Buttons.SunkenButton("Sum avg signal", 0, 3),
            Buttons.SunkenButton("Power",          1, 0),
            Buttons.SunkenButton("Sum power",      1, 1),
            Buttons.SunkenButton("Avg power",      1, 2),
            Buttons.SunkenButton("Sum avg power",  1, 3)
        ))