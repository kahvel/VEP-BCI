from gui_elements.widgets import Buttons, Textboxes
from gui_elements.widgets.frames import Frame
from gui_elements.widgets.frames.tabs import DisableDeleteNotebookTab
import constants as c
import Recording
import os


class RecordNotebookTab(DisableDeleteNotebookTab.Delete):
    def __init__(self, parent, deleteTab, **kwargs):
        DisableDeleteNotebookTab.Delete.__init__(self, parent, c.RECORD_NOTEBOOK_TAB, **kwargs)
        self.addChildWidgets((
            ResultsFrame(self, 0, 0, columnspan=3),
            Textboxes.TimestampTextbox(self, 1, 0),
            Textboxes.DirectoryTextbox(self, 2, 0),
            EegFrame(self, 3, 0, columnspan=3),
            SaveButton(self, 4, 0),
            self.getDeleteButton(4, 1, deleteTab)
        ))

    def saveEegEvent(self, directory):
        if self.saveMe():
            file = open(os.path.join(directory, "results.txt"), "w")
            self.sendEventToChildren(lambda x: x.saveBciSettingsEvent(file))
        else:
            return c.STOP_EVENT_SENDING

    def saveMe(self):
        return self.widgets_dict[c.TRAINING_SAVE_EEG].saveMe()

    def loadEegEvent(self, directory):
        file_name = os.path.join(directory, "results.txt")
        if os.path.isfile(file_name):
            file = open(file_name, "r")
            self.sendEventToChildren(lambda x: x.loadBciSettingsEvent(file))
        else:
            print file_name, "does not exist!"
    
    def addNewRecordingTabEvent(self):
        self.widgets_dict[c.TIMESTAMP_TEXTBOX].setTimestamp()


class SaveButton(Buttons.EventNotebookSaveButton):
    def __init__(self, parent, row, column, **kwargs):
        Buttons.EventNotebookSaveButton.__init__(self, parent, c.TRAINING_SAVE_EEG, row, column, **kwargs)

    def sendSaveEvent(self, file):
        return lambda x: x.saveEegEvent(file)


class EegFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.EEG_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.DisabledTextLabelTextbox(self, c.PACKET_COUNT, 0, 0),
            Textboxes.DisabledTextLabelTextbox(self, c.SAMPLE_COUNT, 0, 2),
        ))
        self.eeg = Recording.Eeg()
        self.features = Recording.Features()
        self.has_features = False

    def recordedEegReceivedEvent(self, eeg):
        self.eeg = eeg
        self.widgets_dict[c.PACKET_COUNT].setValue(eeg.getLength())

    def recordedFeaturesReceivedEvent(self, features):
        self.features = features
        self.widgets_dict[c.SAMPLE_COUNT].setValue(features.getLength())
        self.has_features = True

    def loadEegEvent(self, directory):
        self.eeg.load(directory)
        self.features.load(directory)
        self.has_features = True

    def saveEegEvent(self, directory):
        self.eeg.save(directory)
        self.features.save(directory)

    def getFeaturesEvent(self):
        if self.has_features:  # Last tab has no features
            self.sendEventToRoot(lambda x: x.sendFeaturesToRootEvent(self.features))


class ResultsFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.RECORD_NOTEBOOK_TAB_RESULTS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_DIAGONAL_ELEMENTS, 0, 0),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_OFF_DIAGONAL_ELEMENTS, 0, 2),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_ACCURACY, 0, 4),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_ITR_BIT_PER_TRIAL, 1, 2),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_ITR_BIT_PER_MIN, 1, 4),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_TOTAL_TIME_SECONDS, 2, 0),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_TOTAL_TIME_PACKETS, 2, 2),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_TIME_PER_TARGET, 2, 4),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_MACRO_F1, 3, 0),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_F1, 3, 2, width=25, columnspan=3),
        ))
        self.results = None

    def resultsReceivedEvent(self, results):
        self.results = results
        for key in self.widgets_dict:
            self.widgets_dict[key].setValue(results[key])
