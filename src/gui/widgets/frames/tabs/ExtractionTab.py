from gui.widgets import Checkbutton, Buttons, Textboxes
from gui.widgets.frames.tabs import DisableDeleteNotebookTab
from gui.widgets.frames import Frame, OptionsFrame
from gui.widgets.frames.notebooks import Notebook

import constants as c

import Tkinter


class ExtractionTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, delete_tab, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.EXTRACTION_TAB_TAB, **kwargs)
        self.addChildWidgets((
            ExtractionTabNotebook(self.widget),
            self.getDisableDeleteFrame(3, 0, delete_tab=delete_tab)
        ))


class OptionsTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.EXTRACTION_TAB_OPTIONS_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionsFrame.SensorsFrame(self.widget, 0, 0),
            ExtractionTabButtonFrame(self.widget, 1, 0),
            OptionsFrame.OptionsFrame(self.widget, 2, 0)
        ))


class HarmonicsTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.EXTRACTION_TAB_HARMONICS_TAB, 0, 0, **kwargs)
        Tkinter.Label(self.widget, text="Weight").grid(row=0, column=1)
        Tkinter.Label(self.widget, text="Diff").grid(row=0, column=2)
        for i in range(1, 8):
            checkbutton_name = str(i)
            self.addChildWidgets((
                Checkbutton.Checkbutton(self.widget, checkbutton_name,                       i, 0),
                Textboxes.Textbox      (self.widget, c.HARMONIC_WEIGHT+checkbutton_name,     i, 1),
                Textboxes.Textbox      (self.widget, c.HARMONIC_DIFFERENCE+checkbutton_name, i, 2)
            ))
        Tkinter.Label(self.widget, text="All").grid(row=8, column=0)
        self.addChildWidgets((
            Textboxes.Textbox(self.widget, c.HARMONIC_WEIGHT+c.RESULT_SUM, 8, 1),
            Textboxes.Textbox(self.widget, c.HARMONIC_DIFFERENCE+c.RESULT_SUM, 8, 2)
        ))


class ExtractionTabNotebook(Notebook.Notebook):
    def __init__(self, parent, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.EXTRACTION_TAB_NOTEBOOK, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionsTab(self.widget),
            HarmonicsTab(self.widget)
        ))


class ExtractionTabButtonFrame(OptionsFrame.OptionsFrameFrame):
    def __init__(self, parent, row, column, **kwargs):
        OptionsFrame.OptionsFrameFrame.__init__(self, parent,c.METHODS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton(self.widget, c.PSDA,     0, 0),
            Buttons.SunkenButton(self.widget, c.SUM_PSDA, 0, 1),
            Buttons.SunkenButton(self.widget, c.CCA,      0, 2)
        ))
