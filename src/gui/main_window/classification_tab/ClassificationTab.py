from gui_elements.widgets.frames import Frame, AddingCheckbuttonsFrame
from gui_elements.widgets import Checkbutton, Textboxes, OptionMenu, Buttons
import constants as c

import Tkinter


class CheckbuttonFrame(AddingCheckbuttonsFrame.AddingCheckbuttonsFrame):
    def __init__(self, parent, name, row, column, **kwargs):
        AddingCheckbuttonsFrame.AddingCheckbuttonsFrame.__init__(self, parent, name, row, column, [], **kwargs)

    def sendRecordingNotebookWidgetsEvent(self, recording_notebook_widgets):
        self.setWidgetsNotebook(recording_notebook_widgets)

    def getNotebookWidgetsEvent(self):
        self.sendEventToAll(lambda x: x.getRecordingNotebookWidgetsEvent())

    def addNewRecordingTabEvent(self):
        self.addButton()

    def recordTabRemovedEvent(self, deleted_tab):
        self.deleteButton(deleted_tab)

    def loadEegEvent(self, directory):
        self.addButton()

    def saveBciSettingsEvent(self, file):
        return c.STOP_EVENT_SENDING

    def loadBciSettingsEvent(self, file):
        return c.STOP_EVENT_SENDING


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


class ControlFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.CLASSIFICATION_TAB_CONTROL_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenu(self, c.CLASSIFICATION_TAB_TYPE_OPTION_MENU, 0, 1, c.CLASSIFICATION_TYPE_NAMES),
            Buttons.Button(self, c.CLASSIFICATION_TAB_TRAIN_MODEL, 0, 3, command=self.trainButtonClicked)
        ))

    def trainButtonClicked(self):
        self.sendEventToRoot(lambda x: x.trainButtonClickedEvent())


class OptionsFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.CLASSIFICATION_TAB_OPTIONS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.LabelTextbox(self, c.CLASSIFICATION_TAB_LOOK_BACK_LENGTH, 0, 0, command=int, default_value=1),
            Textboxes.LabelTextbox(self, c.CLASSIFICATION_TAB_CV_FOLDS, 0, 2, command=int, default_value=5),
            Textboxes.LabelTextboxNoValidation(self, c.CLASSIFICATION_TAB_FEATURES_TO_USE, 1, 0, default_value="", width=20, columnspan=3),
        ))


class ClassificationTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_NOTEBOOK_CLASSIFICATION_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            ControlFrame(self, 0, 0),
            OptionsFrame(self, 1, 0),
            LabelledCheckbuttonFrame(self, c.CLASSIFICATION_TAB_RECORDING_FOR_TRAINING, 2, 0),
            LabelledCheckbuttonFrame(self, c.CLASSIFICATION_TAB_RECORDING_FOR_VALIDATION, 3, 0),
            IdentificationOptionsFrame(self, 4, 0),
        ))

    def getClassificationOptionsEvent(self):
        self.sendEventToRoot(lambda x: x.sendClassificationOptionsToRootEvent(self.getValue()), True)
