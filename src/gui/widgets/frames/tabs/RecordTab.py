from gui.widgets import Buttons, OptionMenu, Textboxes
from gui.widgets.frames import Frame
import constants as c
import Savable


class RecordTab(Frame.Frame):
    def __init__(self, parent, **kwargs):
        Frame.Frame.__init__(self, parent, c.RECORD_TAB, 0, 0, **kwargs)
        self.addChildWidgets((
            ResultsFrame(self, 0, 0),
            RecordFrame(self, 1, 0),
        ))


class RecordFrame(Frame.Frame, Savable.Savable, Savable.Loadable):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.RECORD_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            OptionMenu.OptionMenu(self, c.TRAINING_RECORD,    0, 1, c.TRAINING_RECORD_NAMES),
            Buttons.Button       (self, c.TRAINING_SAVE_EEG,  1, 0, command=self.saveEegClicked),
            Buttons.Button       (self, c.TRAINING_LOAD_EEG,  1, 1, command=self.loadEegClicked),
            Buttons.Button       (self, c.TRAINING_RESET_EEG, 1, 2, command=self.resetEegClicked),
        ))

    def saveEegClicked(self):
        self.askSaveFile()

    def loadEegClicked(self):
        self.askLoadFile()

    def resetEegClicked(self):
        self.sendEventToRoot(lambda x: x.resetEegEvent(), True)

    def saveToFile(self, file):
        """
        askSaveFile calls this function when corresponding button is pressed.
        :param file:
        :return:
        """
        self.sendEventToRoot(lambda x: x.saveEegEvent(file), True)

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
            Textboxes.DisabledTextLabelTextbox(self, c.RESULTS_DATA_F1, 3, 2),
        ))
        self.results = None

    def fillResultsFrameEvent(self, results):
        self.results = results
        for key in self.widgets_dict:
            self.widgets_dict[key].setValue(results[key])
