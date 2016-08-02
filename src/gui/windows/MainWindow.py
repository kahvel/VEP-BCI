import constants as c
import os

from gui import ButtonsStateController
from gui.windows import MyWindows
from gui.widgets.frames import MainFrame
import MainFrameButtonCommands
import Savable
import PostOfficeMessageHandler
import InputParser


class AbstractMainWindow(MyWindows.TkWindow, Savable.Savable, Savable.Loadable):
    def __init__(self, connection, default_settings_file_name):
        MyWindows.TkWindow.__init__(self, "VEP-BCI")
        self.connection = connection
        """ @type : connections.ConnectionProcessEnd.MainConnection """
        self.default_settings_file_name = default_settings_file_name
        self.bottom_frame_buttons_states = ButtonsStateController.ButtonsStateController(self, (c.BOTTOM_FRAME,))
        self.message_handler = self.getMessageHandler(self.bottom_frame_buttons_states)
        self.main_frame = self.getMainFrame(self.message_handler)
        self.loadValuesAtStartup()
        self.bottom_frame_buttons_states.setInitialStates()
        self.checkMessages()
        self.mainloop()

    def getMainFrame(self, message_handler):
        raise NotImplementedError("getMainFrame not implemented!")

    def getMessageHandler(self, bottom_frame_buttons_states):
        raise NotImplementedError("getMessageHandler not implemented!")

    def checkMessages(self):
        message = self.connection.receiveMessageInstant()
        if self.message_handler.canHandle(message):
            self.message_handler.handle(message)
        self.after(100, self.checkMessages)

    def loadValuesAtStartup(self):
        import __main__
        try:
            self.main_frame.load(open(os.path.join(os.path.dirname(os.path.abspath(__main__.__file__)), self.default_settings_file_name)))
        except IOError:
            self.main_frame.loadDefaultValue()

    def resetResults(self):
        self.connection.sendMessage(c.RESET_RESULTS_MESSAGE)

    def showResults(self):
        self.connection.sendMessage(c.SHOW_RESULTS_MESSAGE)

    def saveResults(self, file):
        self.connection.sendMessage(c.SAVE_RESULTS_MESSAGE)
        self.connection.sendMessage(file)

    def saveEeg(self, file):
        self.connection.sendMessage(c.SAVE_EEG_MESSAGE)
        self.connection.sendMessage(file)

    def loadEeg(self, file):
        self.connection.sendMessage(c.LOAD_EEG_MESSAGE)
        self.connection.sendMessage(file)

    def resetEeg(self):
        self.connection.sendMessage(c.RESET_EEG_MESSAGE)

    def exit(self):
        self.exitFlag = True
        self.connection.sendExitMessage()
        self.connection.close()
        self.destroy()
        print("Exited main window")

    def saveToFile(self, file):
        self.main_frame.save(file)

    def loadFromFile(self, file):
        self.main_frame.load(file)
        self.bottom_frame_buttons_states.setInitialStates()


class MainWindow(AbstractMainWindow):
    def __init__(self, connection):
        AbstractMainWindow.__init__(self, connection, c.DEFAULT_SETTINGS_FILE_NAME)

    def getMainFrame(self, message_handler):
        button_commands = MainFrameButtonCommands.MainFrameButtonCommands(self, message_handler).commands
        return MainFrame.MainFrame(self, button_commands)

    def getMessageHandler(self, bottom_frame_buttons_states):
        input_parser = InputParser.MainInputParser()
        return PostOfficeMessageHandler.PostOfficeMessageHandler(self, bottom_frame_buttons_states, input_parser)


class TrainingWindow(AbstractMainWindow):
    def __init__(self, connection):
        AbstractMainWindow.__init__(self, connection, c.DEFAULT_TRAINING_SETTINGS_FILE_NAME)

    def getMainFrame(self, message_handler):
        button_commands = MainFrameButtonCommands.MainFrameButtonCommands(self, message_handler).commands
        return MainFrame.TrainingMainFrame(self, button_commands)

    def getMessageHandler(self, bottom_frame_buttons_states):
        input_parser = InputParser.TrainingInputParser()
        return PostOfficeMessageHandler.PostOfficeMessageHandler(self, bottom_frame_buttons_states, input_parser)

    def loadEeg(self, file):
        AbstractMainWindow.loadEeg(self, file)
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
