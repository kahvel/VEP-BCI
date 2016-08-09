from gui_elements.widgets import Buttons, Textboxes
from gui_elements.widgets.frames import Frame
from gui_elements.widgets.frames.tabs import DisableDeleteNotebookTab
import constants as c

import os
import pickle


class ModelsNotebookTab(DisableDeleteNotebookTab.Delete):
    def __init__(self, parent, deleteTab, **kwargs):
        DisableDeleteNotebookTab.Delete.__init__(self, parent, c.MODELS_NOTEBOOK_TAB, **kwargs)
        self.addChildWidgets((
            ModelFrame(self, 0, 0),
            Textboxes.TimestampTextbox(self, 1, 0),
            Textboxes.DirectoryTextbox(self, 2, 0),
            SaveButton(self, 3, 0),
            self.getDeleteButton(3, 1, deleteTab)
        ))

    def saveModelEvent(self, directory):
        if self.saveMe():
            file = open(os.path.join(directory, "results.txt"), "w")
            self.sendEventToChildren(lambda x: x.saveBciSettingsEvent(file))
        else:
            return c.STOP_EVENT_SENDING

    def saveMe(self):
        return self.widgets_dict[c.MODELS_TAB_SAVE_MODEL].saveMe()

    def loadModelEvent(self, directory):
        file_name = os.path.join(directory, "results.txt")
        if os.path.isfile(file_name):
            file = open(file_name, "r")
            self.sendEventToChildren(lambda x: x.loadBciSettingsEvent(file))
        else:
            print file_name, "does not exist!"

    def addNewModelTabEvent(self):
        self.widgets_dict[c.TIMESTAMP_TEXTBOX].setTimestamp()


class SaveButton(Buttons.EventNotebookSaveButton):
    def __init__(self, parent, row, column, **kwargs):
        Buttons.EventNotebookSaveButton.__init__(self, parent, c.MODELS_TAB_SAVE_MODEL, row, column, **kwargs)

    def sendSaveEvent(self, file):
        return lambda x: x.saveModelEvent(file)


class ModelFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.EEG_FRAME, row, column, **kwargs)
        # self.addChildWidgets((
        #
        # ))
        self.model = None

    def loadModelEvent(self, directory):
        self.model = pickle.load(file(os.path.join(directory, "model.pkl")))

    def saveModelEvent(self, directory):
        pickle.Pickler(file(os.path.join(directory, "model.pkl"), "w")).dump(self.model)

    def modelReceivedEvent(self, model):
        self.model = model

    def trainingDataReceivedEvent(self, training_data):
        print training_data

    def trainingLabelsReceivedEvent(self, training_labels):
        print training_labels

    def validationDataReceivedEvent(self, validation_data):
        print validation_data

    def validationLabelsReceivedEvent(self, validation_labels):
        print validation_labels