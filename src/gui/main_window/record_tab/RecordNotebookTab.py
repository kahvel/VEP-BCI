import os

import matplotlib.pyplot as plt

from gui_elements.widgets import Buttons, Textboxes
from gui_elements.widgets.frames import Frame
from gui_elements.widgets.frames.tabs import DisableDeleteNotebookTab
import constants as c
from bci import Recording


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

    def saveResults(self, directory):
        file = open(os.path.join(directory, "results.txt"), "w")
        self.sendEventToChildren(lambda x: x.saveBciSettingsEvent(file))

    def saveAllTabsEvent(self, directory, i):
        directory_name = os.path.join(directory, "rec" + str(i+1))
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        self.saveResults(directory_name)
        self.widgets_dict[c.EEG_FRAME].sendEventToChildren(lambda x: x.saveEegEvent(directory_name))

    def saveEegEvent(self, directory):
        if self.saveMe():
            self.saveResults(directory)
        else:
            return c.STOP_EVENT_SENDING

    def saveMe(self):
        return self.widgets_dict[c.RECORDING_SAVE_TAB].saveMe()

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
        Buttons.EventNotebookSaveButton.__init__(self, parent, c.RECORDING_SAVE_TAB, row, column, **kwargs)

    def sendSaveEvent(self, file):
        return lambda x: x.saveEegEvent(file)


class PlotButton(Buttons.Button):
    """
    Class just to avoid loading and saving value for this button.
    """
    def __init__(self, parent, row, column, **kwargs):
        Buttons.Button.__init__(self, parent, c.PLOT_BUTTON_NAME, row, column, **kwargs)

    def loadBciSettingsEvent(self, file):
        pass

    def saveBciSettingsEvent(self, file):
        pass


class EegFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.EEG_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.DisabledTextLabelTextbox(self, c.PACKET_COUNT, 0, 0),
            Textboxes.DisabledTextLabelTextbox(self, c.SAMPLE_COUNT, 0, 2),
            PlotButton(self, 0, 4, command=self.plotEeg)
        ))
        self.eeg = Recording.Eeg()
        self.features = Recording.Features()
        self.has_features = False
        self.has_eeg = False

    def plotEeg(self, sensors=("O1", "O2", "P7", "P8")):
        x = list(range(0, len(self.eeg.data)))
        plt.figure()
        for i, sensor in enumerate(sensors):
            plt.subplot(len(sensors), 1, i+1)
            plt.plot(x, map(lambda x: x[sensor], self.eeg.data))
        previous_target = None
        for i, target in enumerate(self.eeg.expected_targets):
            if previous_target != target:
                for j, sensor in enumerate(sensors):
                    plt.subplot(len(sensors), 1, j+1)
                    plt.plot(i, self.eeg.data[i][sensor], "o", c="red")
                previous_target = target
        plt.show()

    def getValue(self):
        frame_value = Frame.Frame.getValue(self)
        frame_value.update({c.RECORDING_TAB_RECORDING_DATA: {
            c.RECORDING_TAB_EEG: self.eeg,
            c.RECORDING_TAB_FEATURES: self.features,
        }})
        return frame_value

    def recordedEegReceivedEvent(self, eeg):
        self.eeg = eeg
        self.widgets_dict[c.PACKET_COUNT].setValue(eeg.getLength())
        self.has_eeg = True

    def recordedFeaturesReceivedEvent(self, features):
        self.features = features
        self.widgets_dict[c.SAMPLE_COUNT].setValue(features.getLength())
        self.has_features = True

    def loadEegEvent(self, directory):
        self.eeg.load(directory)
        self.features.load(directory)
        self.has_features = True
        self.has_eeg = True
        # import matplotlib.pyplot as plt  # For plotting certain EEG segments
        # import numpy as np
        # window = 256
        # index = 201
        # time = np.arange(0, window, 1)
        # plt.subplot(2, 1, 1)
        # plt.plot(time, self.eeg.getColumnsAsIntegers(self.eeg.data)["O1"][(index-1)*32:(index-1)*32+window])
        # plt.subplot(2, 1, 2)
        # plt.plot(time, self.eeg.getColumnsAsIntegers(self.eeg.data)["O2"][(index-1)*32:(index-1)*32+window])
        # plt.show()

    def saveEegAndFeatures(self, directory):
        self.eeg.save(directory)
        self.features.save(directory)

    def saveEegEvent(self, directory):
        self.saveEegAndFeatures(directory)

    def getFeaturesEvent(self):
        if self.has_features:  # Last tab has no features
            self.sendEventToRoot(lambda x: x.sendFeaturesToRootEvent(self.features))

    def getEegEvent(self):
        if self.has_eeg:
            self.sendEventToRoot(lambda x: x.sendEegToRootEvent(self.eeg))


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
