__author__ = 'Anti'

from widgets import Checkbutton, Buttons, Textboxes, OptionMenu
from frames import Frame, SameTabsNotebookTab


class ExtractionTab(SameTabsNotebookTab.SameTabsNotebookTab):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebookTab.SameTabsNotebookTab.__init__(self, parent, "ExtractionTab", row, column, **kwargs)
        self.addChildWidgets((
            SensorsFrame(self.widget, 0, 0),
            ExtractionTabButtonFrame(self.widget, 1, 0),
            OptionsFrame(self.widget, 2, 0),
            self.getDisableDeleteFrame(3, 0, delete_tab=kwargs["delete_tab"])
        ))


class PlotTab(SameTabsNotebookTab.SameTabsNotebookTab):
    def __init__(self, parent, row, column, **kwargs):
        SameTabsNotebookTab.SameTabsNotebookTab.__init__(self, parent, "PlotTab", row, column, **kwargs)
        self.addChildWidgets((
            SensorsFrame(self.widget, 0, 0),
            PlotTabButtonFrame(self.widget, 1, 0),
            OptionsFrame(self.widget, 2, 0),
            self.getDisableDeleteFrame(3, 0, delete_tab=kwargs["delete_tab"])
        ))


class SensorsFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, "SensorsFrame", row, column, **kwargs)
        self.addChildWidgets((
            Checkbutton.Checkbutton(self.widget, "AF3", 0, 0, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, "F7",  0, 1, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, "F3",  0, 2, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, "FC5", 0, 3, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, "T7",  0, 4, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, "P7",  0, 5, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, "O1",  0, 6, pady=0, padx=0, default_value=1),
            Checkbutton.Checkbutton(self.widget, "O2",  1, 0, pady=0, padx=0, default_value=1),
            Checkbutton.Checkbutton(self.widget, "P8",  1, 1, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, "T8",  1, 2, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, "FC6", 1, 3, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, "F4",  1, 4, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, "F8",  1, 5, pady=0, padx=0),
            Checkbutton.Checkbutton(self.widget, "AF4", 1, 6, pady=0, padx=0)
        ))


class OptionsFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, "OptionsFrame", row, column, **kwargs)
        windows = ("None", "Hanning", "Hamming", "Blackman", "Kaiser", "Bartlett")
        self.addChildWidgets((
            Checkbutton.Checkbutton(self.widget, "Normalise", 0, 0,                      columnspan=2),
            Checkbutton.Checkbutton(self.widget, "Detrend",   0, 2,                      columnspan=2),
            Checkbutton.Checkbutton(self.widget, "Filter",    0, 4, command=self.disableFilter,      columnspan=2),
            Textboxes.LabelTextbox (self.widget, "Step",      1, 0, command=int,    default_value=32),
            Textboxes.LabelTextbox (self.widget, "Length",    1, 2, command=int,    default_value=512),
            Textboxes.LabelTextbox (self.widget, "From",      3, 0, command=float, allow_zero=True, default_disability=True, default_disablers=["Filter"]),
            Textboxes.LabelTextbox (self.widget, "To",        3, 2, command=float, allow_zero=True, default_disability=True, default_disablers=["Filter"]),
            Textboxes.LabelTextbox (self.widget, "Taps",      3, 4, command=int,   allow_zero=True, default_disability=True, default_disablers=["Filter"]),
            Textboxes.LabelTextbox (self.widget, "Beta",      4, 2, command=int,   allow_zero=True, default_disability=True, default_disablers=["Window"]),
            OptionMenu.OptionMenu  (self.widget, "Window",    4, 0, command=self.disableWindow, values=windows),
            Textboxes.LabelTextbox (self.widget, "Break",     4, 4, command=int,   allow_zero=True)
        ))

    def disableFilter(self):
        self.conditionalDisabling(
            self.widgets_dict["Filter"],
            1,
            (
                self.widgets_dict["From"],
                self.widgets_dict["To"],
                self.widgets_dict["Taps"]
            )
        )

    def disableWindow(self):
        self.conditionalDisabling(
            self.widgets_dict["Window"],
            "Kaiser",
            (
                self.widgets_dict["Beta"],
            )
        )


class ExtractionTabButtonFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, "ExtractionTabButtonFrame", row, column, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton(self.widget, "PSDA",     0, 0),
            Buttons.SunkenButton(self.widget, "Sum PSDA", 0, 1),
            Buttons.SunkenButton(self.widget, "CCA",      0, 2),
            Buttons.SunkenButton(self.widget, "Both",     0, 3),
            Buttons.SunkenButton(self.widget, "Sum Both", 0, 4),
        ))


class PlotTabButtonFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, "PlotTabButtonFrame", row, column, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton(self.widget, "Signal",         0, 0),
            Buttons.SunkenButton(self.widget, "Sum signal",     0, 1),
            Buttons.SunkenButton(self.widget, "Avg signal",     0, 2),
            Buttons.SunkenButton(self.widget, "Sum avg signal", 0, 3),
            Buttons.SunkenButton(self.widget, "Power",          1, 0),
            Buttons.SunkenButton(self.widget, "Sum power",      1, 1),
            Buttons.SunkenButton(self.widget, "Avg power",      1, 2),
            Buttons.SunkenButton(self.widget, "Sum avg power",  1, 3)
        ))