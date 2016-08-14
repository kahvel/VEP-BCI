from gui_elements.widgets.frames.notebooks import Notebook
from gui_elements.widgets.frames import Frame, OptionsFrame, AddingCheckbuttonsFrame
from gui_elements.widgets import Checkbutton, Textboxes, Buttons
import constants as c

import Tkinter


class ExtractionNotebookTabNotebook(Notebook.Notebook):
    def __init__(self, parent, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.EXTRACTION_TAB_NOTEBOOK, 0, 0, **kwargs)
        self.addChildWidgets((
            ActiveTab(self),
            OptionsTab(self),
            HarmonicsTab(self)
        ))


class HarmonicsTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.EXTRACTION_TAB_HARMONICS_TAB, 0, 0, **kwargs)
        Tkinter.Label(self.widget, text="              Weight  Diff").grid(row=0, column=0)
        for i in range(1, 8):
            checkbutton_name = str(i)+"      "
            self.addChildWidgets((HarmonicFrame(self, checkbutton_name, i > 3, i),))
        self.addChildWidgets((HarmonicFrame(self, c.RESULT_SUM, False, 8),))


class HarmonicFrame(Frame.Frame):
    def __init__(self, parent, name, disabled, row, **kwargs):
        Frame.Frame.__init__(self, parent, name, row, 0, padx=0, pady=0, **kwargs)
        self.addChildWidgets((
            Checkbutton.Checkbutton(self, name,                  0, 0, command=self.enableTextboxes, default_value=not disabled),
            Textboxes.Textbox      (self, c.EXTRACTION_TAB_HARMONIC_WEIGHT,     0, 1, default_disability=disabled, default_disablers=self.getDefaultDisabler(disabled), allow_zero=True),
            Textboxes.Textbox      (self, c.EXTRACTION_TAB_HARMONIC_DIFFERENCE, 0, 2, default_disability=disabled, default_disablers=self.getDefaultDisabler(disabled), allow_zero=True),
        ))

    def enableTextboxes(self):
        self.conditionalEnabling(
            self.widgets_dict[self.name],
            (1,),
            (self.widgets_dict[c.EXTRACTION_TAB_HARMONIC_WEIGHT], self.widgets_dict[c.EXTRACTION_TAB_HARMONIC_DIFFERENCE])
        )

    def getDefaultDisabler(self, disabled):
        return [self.name] if disabled else []


class ActiveTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.EXTRACTION_TAB_ACTIVE_TAB, 0, 0, **kwargs)
        Tkinter.Label(self.widget, text="Methods").grid(row=0, column=0)
        Tkinter.Label(self.widget, text="Sensors").grid(row=2, column=0)
        Tkinter.Label(self.widget, text="Targets").grid(row=4, column=0)
        self.addChildWidgets((
            ExtractionTabButtonFrame(self, 1, 0),
            OptionsFrame.SensorsFrame(self, 3, 0),
            TargetsFrame(self, 5, 0),
        ))


class OptionsTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.EXTRACTION_TAB_OPTIONS_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionsFrame.OptionsFrame(self, 2, 0),
        ))


class TargetsFrame(AddingCheckbuttonsFrame.PlusTabNotebookAddingCheckbuttonFrame):
    def __init__(self, parent, row, column, **kwargs):
        AddingCheckbuttonsFrame.PlusTabNotebookAddingCheckbuttonFrame.__init__(self, parent, c.EXTRACTION_TAB_TARGETS_FRAME, row, column, **kwargs)

    def sendTargetNotebookWidgetsEvent(self, targets_notebook_widgets):
        self.setWidgetsNotebook(targets_notebook_widgets)

    def getNotebookWidgetsEvent(self):
        self.sendEventToAll(lambda x: x.getTargetNotebookWidgetsEvent())

    def targetAddedEvent(self):
        self.addButton(False)

    def targetRemovedEvent(self, deleted_tab):
        self.deleteButton(deleted_tab)

    def targetDisabledEvent(self, tabs, current_tab):
        self.disableButton(current_tab)

    def targetEnabledEvent(self, tabs, current_tab):
        self.enableButton(current_tab)


class ExtractionTabButtonFrame(OptionsFrame.OptionsFrameFrame):
    def __init__(self, parent, row, column, **kwargs):
        OptionsFrame.OptionsFrameFrame.__init__(self, parent, c.METHODS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.SunkenButton(self, c.PSDA,     0, 0),
            Buttons.SunkenButton(self, c.SUM_PSDA, 0, 1),
            Buttons.SunkenButton(self, c.CCA,      0, 2),
            Buttons.SunkenButton(self, c.LRT,      0, 3),
            Buttons.SunkenButton(self, c.SNR_PSDA, 0, 4)
        ))
