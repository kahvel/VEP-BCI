__author__ = 'Anti'

import tkFileDialog
import constants as c

from gui.main_window import MyWindows
from gui.widgets.frames import MainFrame


class MainWindow(MyWindows.TkWindow):
    def __init__(self, connection):
        MyWindows.TkWindow.__init__(self, "VEP-BCI", 310, 500)
        self.exitFlag = False
        self.connection = connection
        """ @type : connections.ConnectionProcessEnd.MainConnection """
        self.main_frame = MainFrame.MainFrame(self, (
            (
                self.start,
                self.stop,
                self.setup,
                self.askSaveFile,
                self.askLoadFile,
                self.exit
            ),
            (
                (
                    self.showResults,
                    self.resetResults,
                    self.saveResults
                ),
                self.connection.sendMessage
            )
        )
        )
        self.loadValues(c.DEFAULT_FILE)
        self.disableButton(c.START_BUTTON)
        self.disableButton(c.STOP_BUTTON)
        self.setup_options = None
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.mainloop()

    def mainloop(self, n=0):
        while True:
            message = self.connection.receiveMessagePoll(0.1)
            if message == c.STOP_MESSAGE:
                self.stop()
            elif message == c.SUCCESS_MESSAGE:  # Setup was successful
                self.enableButton(c.START_BUTTON)
            elif message == c.FAIL_MESSAGE:  # Setup failed
                self.disableButton(c.START_BUTTON)
            if not self.exitFlag:
                self.update()
            else:
                self.connection.close()
                return

    def loadValues(self, default_file_name):
        try:
            self.main_frame.load(open(default_file_name))
        except IOError:
            self.main_frame.loadDefaultValue()

    def resetResults(self):
        self.connection.sendMessage(c.RESET_RESULTS_MESSAGE)

    def showResults(self):
        self.connection.sendMessage(c.SHOW_RESULTS_MESSAGE)

    def saveResults(self):
        self.connection.sendMessage(c.SAVE_RESULTS_MESSAGE)

    def getFrequencies(self, enabled_targets):
        return {key: target[c.DATA_FREQ] for key, target in enabled_targets.items()}

    def getHarmonics(self, data):
        result = []
        for target in data:
            result.append(tuple(map(int, target[c.TARGET_HARMONICS].split(","))))
        return result

    def getTargetData(self, targets_data):
        return {key: value.values()[0] for key, value in targets_data.items()}

    def getData(self, all_data):
        target_data = self.getTargetData(all_data[c.TARGETS_NOTEBOOK])
        return {
            c.DATA_BACKGROUND: all_data[c.WINDOW_TAB],
            c.DATA_TARGETS: target_data,
            c.DATA_FREQS: self.getFrequencies(target_data),
            c.DATA_PLOTS: all_data[c.PLOT_NOTEBOOK].values(),
            c.DATA_EXTRACTION: all_data[c.EXTRACTION_NOTEBOOK].values(),
            c.DATA_TEST: all_data[c.TEST_TAB],
            c.DATA_HARMONICS: self.getHarmonics(target_data.values()),
            c.DATA_ROBOT: {c.DISABLE: all_data[c.ROBOT_TAB][c.DISABLE]},
            c.DATA_EMOTIV: {c.DISABLE: all_data[c.EMOTIV_TAB][c.DISABLE]}
        }

    def exit(self):
        self.exitFlag = True
        print("Exiting main window")
        self.connection.sendExitMessage()
        self.destroy()

    def setup(self):
        not_validated = self.main_frame.getNotValidated()
        self.setup_options = self.getData(self.main_frame.getValue()[c.MAIN_NOTEBOOK])
        print(self.setup_options)
        if len(not_validated) != 0:
            print(not_validated)
        else:
            self.connection.sendSetupMessage()
            self.connection.sendMessage(self.setup_options)

    def disableButton(self, button_name):
        self.main_frame.widgets_dict[c.BOTTOM_FRAME].disableButton(button_name)

    def enableButton(self, button_name):
        self.main_frame.widgets_dict[c.BOTTOM_FRAME].enableButton(button_name)

    def start(self):
        if self.setup_options != self.getData(self.main_frame.getValue()[c.MAIN_NOTEBOOK]):
            print("Warning: options were changed, but setup was not clicked")
        self.disableButton(c.SETUP_BUTTON)
        self.disableButton(c.START_BUTTON)
        self.enableButton(c.STOP_BUTTON)
        self.connection.sendStartMessage()

    def stop(self):
        self.enableButton(c.SETUP_BUTTON)
        self.enableButton(c.START_BUTTON)
        self.disableButton(c.STOP_BUTTON)
        self.connection.sendStopMessage()

    # Save and Load

    def askSaveFile(self):
        self.saveFile(tkFileDialog.asksaveasfile())

    def saveFile(self, file):
        if file is not None:
            self.main_frame.save(file)
            file.close()

    def askLoadFile(self):
        self.loadFile(tkFileDialog.askopenfile())

    def loadFile(self, file):
        if file is not None:
            self.main_frame.load(file)
            file.close()
