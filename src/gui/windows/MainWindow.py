import constants as c
import __main__
import os

from gui.windows import MyWindows
from gui.widgets.frames import MainFrame
import Savable
import InputParser


class MainWindow(MyWindows.TkWindow, Savable.Savable, Savable.Loadable):
    def __init__(self, connection):
        MyWindows.TkWindow.__init__(self, "VEP-BCI")
        self.connection = connection
        """ @type : connections.ConnectionProcessEnd.MainConnection """
        button_commands = {
            c.BOTTOM_FRAME: (
                    self.start,
                    self.stop,
                    self.setup,
                    self.askSaveFile,
                    self.askLoadFile,
                    self.exit
            ),
            c.TEST_TAB: (
                self.showResults,
                self.resetResults,
                self.saveResults
            ),
            c.ROBOT_TAB: (
                lambda: self.connection.sendMessage(c.MOVE_FORWARD),
                lambda: self.connection.sendMessage(c.MOVE_BACKWARD),
                lambda: self.connection.sendMessage(c.MOVE_RIGHT),
                lambda: self.connection.sendMessage(c.MOVE_LEFT),
                lambda: self.connection.sendMessage(c.MOVE_STOP),
            ),
            c.TRAINING_TAB: (
                self.saveEeg,
                self.loadEeg
            )
        }
        self.main_frame = MainFrame.MainFrame(self, button_commands)
        self.input_parser = InputParser.InputParser()
        self.loadValuesAtStartup()
        self.disableButton(c.START_BUTTON)
        self.disableButton(c.STOP_BUTTON)
        self.setup_options = None
        self.checkMessages()
        self.mainloop()

    def checkMessages(self):
        message = self.connection.receiveMessageInstant()
        if message == c.STOP_MESSAGE:
            self.stop()
        elif message == c.SUCCESS_MESSAGE:  # Setup was successful
            self.enableButton(c.START_BUTTON)
        elif message == c.FAIL_MESSAGE:  # Setup failed
            self.disableButton(c.START_BUTTON)
        if not self.exitFlag:
            self.after(100, self.checkMessages)

    def loadValuesAtStartup(self):
        try:
            self.main_frame.load(open(os.path.join(os.path.dirname(os.path.abspath(__main__.__file__)), c.DEFAULT_FILE)))
        except IOError:
            self.main_frame.loadDefaultValue()

    def resetResults(self):
        self.connection.sendMessage(c.RESET_RESULTS_MESSAGE)

    def showResults(self):
        self.connection.sendMessage(c.SHOW_RESULTS_MESSAGE)

    def saveResults(self, file):
        self.connection.sendMessage(c.SAVE_RESULTS_MESSAGE)
        result_string = self.connection.receiveMessageBlock()
        file.write(result_string)

    def saveEeg(self, file):
        self.connection.sendMessage(c.SAVE_EEG_MESSAGE)
        result_string = self.connection.receiveMessageBlock()
        file.write(result_string)

    def loadEeg(self, file):
        self.connection.sendMessage(c.LOAD_EEG_MESSAGE)
        self.connection.sendMessage(file.read())

    def exit(self):
        self.exitFlag = True
        self.connection.sendExitMessage()
        self.connection.close()
        self.destroy()
        print("Exited main window")

    def setup(self):
        not_validated = self.main_frame.getNotValidated()
        self.setup_options = self.input_parser.parseData(self.main_frame.getValue()[c.MAIN_NOTEBOOK])
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
        if self.setup_options != self.input_parser.parseData(self.main_frame.getValue()[c.MAIN_NOTEBOOK]):
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

    def save(self, file):
        self.main_frame.save(file)

    def load(self, file):
        self.main_frame.load(file)
