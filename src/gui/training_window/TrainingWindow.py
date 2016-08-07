from gui.main_window import MainFrame
from gui import AbstractMainWindow
import PostOfficeMessageHandler
from parsers import InputParser
import constants as c


class TrainingWindow(AbstractMainWindow.AbstractMainWindow):
    def __init__(self, connection):
        AbstractMainWindow.AbstractMainWindow.__init__(self, connection, c.DEFAULT_TRAINING_SETTINGS_FILE_NAME)

    def getMainFrame(self):
        return MainFrame.TrainingMainFrame(self)

    def getMessageHandler(self, main_frame, bottom_frame_buttons_states, connection):
        input_parser = InputParser.TrainingInputParser()
        return PostOfficeMessageHandler.PostOfficeMessageHandler(main_frame, bottom_frame_buttons_states, input_parser, connection)

    def loadEeg(self, file):  # TODO this is broken due to new recording system
        AbstractMainWindow.AbstractMainWindow.loadEeg(self, file)
        self.removeAllTargets()
        file.seek(0)
        self.addTargets(file)

    def addTargets(self, file):
        split_content = file.read().split(";")
        packets = eval(split_content[0])
        target_freqs = packets[0][c.EEG_RECORDING_FREQS]
        for _ in range(len(target_freqs)):
            self.main_frame.targetAdded()

    def removeAllTargets(self):
        try:
            while True:
                self.main_frame.targetRemoved(0)
        except IndexError:
            pass
