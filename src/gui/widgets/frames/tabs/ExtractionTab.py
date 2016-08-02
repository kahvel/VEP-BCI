from gui.widgets import Checkbutton, Buttons, Textboxes
from gui.widgets.frames.tabs import DisableDeleteNotebookTab
from gui.widgets.frames import Frame, OptionsFrame
from gui.widgets.frames.notebooks import Notebook

import constants as c

import Tkinter


class ExtractionTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, deleteTab, target_notebook_widgets, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.EXTRACTION_TAB_TAB, **kwargs)
        self.addChildWidgets((
            ExtractionTabNotebook(self, target_notebook_widgets),
            self.getDisableDeleteFrame(3, 0, deleteTab)
        ))


class OptionsTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.EXTRACTION_TAB_OPTIONS_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            OptionsFrame.OptionsFrame(self, 2, 0),
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
            Textboxes.Textbox      (self, c.HARMONIC_WEIGHT,     0, 1, default_disability=disabled, default_disablers=self.getDefaultDisabler(disabled), allow_zero=True),
            Textboxes.Textbox      (self, c.HARMONIC_DIFFERENCE, 0, 2, default_disability=disabled, default_disablers=self.getDefaultDisabler(disabled), allow_zero=True),
        ))

    def enableTextboxes(self):
        self.conditionalDisabling(
            self.widgets_dict[self.name],
            (1,),
            (self.widgets_dict[c.HARMONIC_WEIGHT], self.widgets_dict[c.HARMONIC_DIFFERENCE])
        )

    def getDefaultDisabler(self, disabled):
        return [self.name] if disabled else []


class ActiveTab(Frame.Frame):
    def __init__(self, parent, target_notebook_widgets, **kwargs):
        Frame.Frame.__init__(self, parent, c.EXTRACTION_TAB_ACTIVE_TAB, 0, 0, **kwargs)
        Tkinter.Label(self.widget, text="Methods").grid(row=0, column=0)
        Tkinter.Label(self.widget, text="Sensors").grid(row=2, column=0)
        Tkinter.Label(self.widget, text="Targets").grid(row=4, column=0)
        self.addChildWidgets((
            ExtractionTabButtonFrame(self, 1, 0),
            OptionsFrame.SensorsFrame(self, 3, 0),
            TargetsFrame(self, 5, 0, target_notebook_widgets),
        ))


class TargetsFrame(Frame.Frame):
    def __init__(self, parent, row, column, target_notebook_widgets, **kwargs):
        Frame.Frame.__init__(self, parent, c.EXTRACTION_TAB_TARGETS_FRAME, row, column, **kwargs)
        self.disabled_tabs = []
        self.target_notebook_widgets = target_notebook_widgets

    def loadDefaultValue(self):
        Frame.Frame.loadDefaultValue(self)
        for widget in self.target_notebook_widgets:
            self.targetAdded(widget.disabled)

    def addOption(self, option, disabled, state):
        new_widget = Checkbutton.Checkbutton(self, str(option), (option-1) // 7, (option-1) % 7, default_value=state, padx=0, pady=0)
        self.addChildWidgets((new_widget,))
        new_widget.loadDefaultValue()
        if disabled:
            new_widget.disable("TargetTab")

    def addDefaultOptions(self):
        pass

    def addTargetOptions(self, button_states):
        for i, disabled in enumerate(self.disabled_tabs):
            self.addOption(i+1, disabled, button_states[i])

    def targetAdded(self, disabled=False):
        self.disabled_tabs.append(disabled)
        self.addOption(len(self.disabled_tabs), disabled, 1)

    def deleteOptions(self):
        for i in range(len(self.widgets_list)-1, -1, -1):
            self.removeWidget(self.widgets_list[i])

    def getCheckbuttonStates(self, deleted_tab):
        states = []
        for i in range(len(self.widgets_list)):
            if i != deleted_tab:
                states.append(self.widgets_list[i].getValue())
        return states

    def deleteAndAddAll(self, deleted_tab):
        button_states = self.getCheckbuttonStates(deleted_tab)
        self.deleteOptions()
        self.addDefaultOptions()
        self.addTargetOptions(button_states)

    def targetRemoved(self, deleted_tab):
        del self.disabled_tabs[deleted_tab]
        self.deleteAndAddAll(deleted_tab)

    def targetDisabled(self, tabs, current_tab):
        self.widgets_list[current_tab].disable("TargetTab")
        self.disabled_tabs[current_tab] = True

    def targetEnabled(self, tabs, current_tab):
        self.widgets_list[current_tab].enable("TargetTab")
        self.disabled_tabs[current_tab] = False

    def save(self, file):
        file.write(str(list(int(value) for value in self.disabled_tabs)).strip("[]") + "\n")
        Frame.Frame.save(self, file)

    def load(self, file):
        disabled_tabs = file.readline().strip("\n")
        disabled_tabs_str = disabled_tabs.split(", ") if disabled_tabs != "" else []
        self.disabled_tabs = list(int(value) for value in disabled_tabs_str)
        self.deleteOptions()
        for i, disabled in enumerate(self.disabled_tabs):
            self.addOption(i+1, disabled, 1)
        Frame.Frame.load(self, file)


class ExtractionTabNotebook(Notebook.Notebook):
    def __init__(self, parent, target_notebook_widgets, **kwargs):
        Notebook.Notebook.__init__(self, parent, c.EXTRACTION_TAB_NOTEBOOK, 0, 0, **kwargs)
        self.addChildWidgets((
            ActiveTab(self, target_notebook_widgets),
            OptionsTab(self),
            HarmonicsTab(self)
        ))


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
