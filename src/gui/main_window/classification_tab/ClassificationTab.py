from gui_elements.widgets.frames import Frame, AddingCheckbuttonsFrame
from gui_elements.widgets import Checkbutton, Textboxes
import constants as c

import Tkinter


class CheckbuttonFrame(AddingCheckbuttonsFrame.AddingCheckbuttonsFrame):
    def __init__(self, parent, name, row, column, **kwargs):
        AddingCheckbuttonsFrame.AddingCheckbuttonsFrame.__init__(self, parent, name, row, column, [], **kwargs)

    def trialEndedEvent(self):
        self.addButton()

    def recordTabRemoved(self, deleted_tab):
        self.deleteButton(deleted_tab)

    def loadEegEvent(self, directory):
        self.addButton()


class LabelledCheckbuttonFrame(Frame.Frame):
    def __init__(self, parent, name, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, name, row, column, **kwargs)
        Tkinter.Label(self.widget, text=name).grid(row=row, column=column, padx=self.padx, pady=self.pady, columnspan=1)
        self.addChildWidgets((
            CheckbuttonFrame(self, name, row, column+1),
        ))


class IdentificationOptionsFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.CLASSIFICATION_TAB_FILTER_OPTIONS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            ResultFilterFrame(self, c.CLASSIFICATION_TAB_RESULT_FILTER_FRAME,      2, 0, columnspan=2),
            ResultFilterFrame(self, c.CLASSIFICATION_TAB_PREV_RESULT_FILTER_FRAME, 3, 0, columnspan=2),
        ))


class ResultFilterFrame(Frame.Frame):
    def __init__(self, parent, name, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, name, row, column, **kwargs)
        Tkinter.Label(self.widget, text=name).grid(row=0, column=0)
        self.addChildWidgets((
            Checkbutton.Checkbutton(self, c.CLASSIFICATION_TAB_ALWAYS_DELETE,    0, 2, columnspan=2),
            Textboxes.LabelTextbox (self, c.CLASSIFICATION_TAB_RESULT_COUNTER,   1, 0, default_value=1),
            Textboxes.LabelTextbox (self, c.CLASSIFICATION_TAB_RESULT_THRESHOLD, 1, 2, allow_zero=True),
        ))


class ClassificationTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_NOTEBOOK_CLASSIFICATION_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            LabelledCheckbuttonFrame(self, c.CLASSIFICATION_TAB_RECORDING_FOR_TRAINING, 1, 0),
            LabelledCheckbuttonFrame(self, c.CLASSIFICATION_TAB_RECORDING_FOR_VALIDATION, 2, 0),
            IdentificationOptionsFrame(self, 3, 0),
        ))
