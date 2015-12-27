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
        Tkinter.Label(self.widget, text="              Weight  Diff").grid(row=0, column=0)
        for i in range(1, 8):
            checkbutton_name = str(i)+"      "
            self.addChildWidgets((HarmonicFrame(self.widget, checkbutton_name, i > 3, i),))
        self.addChildWidgets((HarmonicFrame(self.widget, c.RESULT_SUM, False, 8),))


class HarmonicFrame(Frame.Frame):
    def __init__(self, parent, name, disabled, row, **kwargs):
        Frame.Frame.__init__(self, parent, name, row, 0, padx=0, pady=0, **kwargs)
        self.addChildWidgets((
            Checkbutton.Checkbutton(self.widget, name,                  0, 0, command=self.enableTextboxes, default_value=not disabled),
            Textboxes.Textbox      (self.widget, c.HARMONIC_WEIGHT,     0, 1, default_disability=disabled, default_disablers=self.getDefaultDisabler(disabled)),
            Textboxes.Textbox      (self.widget, c.HARMONIC_DIFFERENCE, 0, 2, default_disability=disabled, default_disablers=self.getDefaultDisabler(disabled))
        ))

    def enableTextboxes(self):
        self.conditionalDisabling(
            self.widgets_dict[self.name],
            (1,),
            (self.widgets_dict[c.HARMONIC_WEIGHT], self.widgets_dict[c.HARMONIC_DIFFERENCE])
        )

    def getDefaultDisabler(self, disabled):
        return [self.name] if disabled else []


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
