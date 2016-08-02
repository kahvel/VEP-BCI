import constants as c
import os

from gui import ButtonsStateController, MessageHandler
from gui.windows import MyWindows
from gui.widgets.frames import MainFrame
import Savable
import PostOfficeMessageHandler
import InputParser


class AbstractMainWindow(MyWindows.TkWindow, Savable.Savable, Savable.Loadable):
    def __init__(self, connection, default_settings_file_name):
        MyWindows.TkWindow.__init__(self, "VEP-BCI")
        Savable.Savable.__init__(self)
        Savable.Loadable.__init__(self)
        self.connection = connection
        self.main_frame = self.getMainFrame()
        button_state_controller = ButtonsStateController.ButtonsStateController(self.main_frame, (c.BOTTOM_FRAME,))
        self.message_handler = MessageHandler.MainWindowMessageHandler(
            connection,
            self.getMessageHandler(self.main_frame, button_state_controller, connection),
            self.main_frame,
            self,
            button_state_controller
        )
        self.default_settings_file_name = default_settings_file_name
        self.loadValuesAtStartup()
        button_state_controller.setInitialStates()
        self.checkMessages()
        self.mainloop()

    def getMainFrame(self):
        raise NotImplementedError("getMainFrame not implemented!")

    def getMessageHandler(self, main_frame, bottom_frame_buttons_states, connection):
        raise NotImplementedError("getMessageHandler not implemented!")

    def checkMessages(self):
        self.message_handler.checkPostOfficeMessages()
        self.after(100, self.checkMessages)

    def getDefaultSettingsFile(self):
        import __main__
        return open(os.path.join(os.path.dirname(os.path.abspath(__main__.__file__)), self.default_settings_file_name))

    def loadValuesAtStartup(self):
        try:
            self.main_frame.load(self.getDefaultSettingsFile())
        except IOError:
            self.main_frame.loadDefaultValue()

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

    def sendEventToRoot(self, function, needs_stopped_state=False):
        self.message_handler.sendEventToRoot(function, needs_stopped_state)


class MainWindow(AbstractMainWindow):
    def __init__(self, connection):
        AbstractMainWindow.__init__(self, connection, c.DEFAULT_SETTINGS_FILE_NAME)

    def getMainFrame(self):
        return MainFrame.MainFrame(self)

    def getMessageHandler(self, main_frame, bottom_frame_buttons_states, connection):
        input_parser = InputParser.MainInputParser()
        return PostOfficeMessageHandler.PostOfficeMessageHandler(main_frame, bottom_frame_buttons_states, input_parser, connection)


class TrainingWindow(AbstractMainWindow):
    def __init__(self, connection):
        AbstractMainWindow.__init__(self, connection, c.DEFAULT_TRAINING_SETTINGS_FILE_NAME)

    def getMainFrame(self):
        return MainFrame.TrainingMainFrame(self)

    def getMessageHandler(self, main_frame, bottom_frame_buttons_states, connection):
        input_parser = InputParser.TrainingInputParser()
        return PostOfficeMessageHandler.PostOfficeMessageHandler(main_frame, bottom_frame_buttons_states, input_parser, connection)

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
