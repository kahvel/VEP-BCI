from gui.widgets import Buttons, Textboxes
from gui.widgets.frames import Frame
from gui.widgets.frames.tabs import DisableDeleteNotebookTab
import constants as c
import Savable
import datetime
import time
import os


class RecordTab(DisableDeleteNotebookTab.Delete):
    def __init__(self, parent, deleteTab, **kwargs):
        DisableDeleteNotebookTab.Delete.__init__(self, parent, c.RECORD_TAB, **kwargs)
        self.addChildWidgets((
            ResultsFrame(self, 0, 0),
            RecordFrame(self, 1, 0),
            TimestampFrame(self, 2, 0),
            self.getDeleteButton(3, 0, deleteTab),
        ))

    def saveEegEvent(self, directory):
        if self.saveMe():
            file = open(os.path.join(directory, "file.txt"), "w")
            self.sendEventToChildren(lambda x: x.saveBciSettingsEvent(file))

    def saveMe(self):
        return self.widgets_dict[c.RECORD_FRAME].saveMe()


class TimestampFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.TIMESTAMP_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_TIMESTAMP, 0, 0, width=30, columnspan=3),
        ))

    def trialEndedEvent(self):
        self.widgets_dict[c.RESULTS_DATA_TIMESTAMP].setValue(self.getTimestamp())

    def getTimestamp(self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S %d.%m.%Y')


class RecordFrame(Frame.Frame, Savable.SavableDirectory, Savable.Loadable):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.RECORD_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self, c.TRAINING_SAVE_EEG,  1, 0, command=self.saveEegClicked),
            Buttons.Button(self, c.TRAINING_LOAD_EEG,  1, 1, command=self.loadEegClicked),
        ))
        self.save_me = False

    def saveMe(self):
        return self.save_me

    def saveEegClicked(self):
        self.askSaveFile()

    def loadEegClicked(self):
        self.askLoadFile()

    def saveToFile(self, file):
        """
        askSaveFile calls this function when corresponding button is pressed.
        :param file:
        :return:
        """
        self.save_me = True
        self.sendEventToRoot(lambda x: x.saveEegEvent(file), True)
        self.save_me = False

    def loadFromFile(self, file):
        """
        askLoadFile calls this function when corresponding button is pressed.
        :param file:
        :return:
        """
        self.sendEventToRoot(lambda x: x.loadEegEvent(file), True)


class ResultsFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.RESULTS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_TRUE_POSITIVES, 0, 0),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_FALSE_POSITIVES, 0, 2),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_PRECISION, 0, 4),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_ITR_BIT_PER_TRIAL, 1, 2),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_ITR_BIT_PER_MIN, 1, 4),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_TOTAL_TIME_SECONDS, 2, 0),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_TOTAL_TIME_PACKETS, 2, 2),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_TIME_PER_TARGET, 2, 4),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_MACRO_F1, 3, 0),
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_F1, 3, 2, width=25, columnspan=3),
        ))
        self.results = None

    def fillResultsFrameEvent(self, results):
        self.results = results
        for key in self.widgets_dict:
            self.widgets_dict[key].setValue(results[key])
