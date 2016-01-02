import constants as c
import __main__
import os

from gui import ButtonsStateController
from gui.windows import MyWindows
from gui.widgets.frames import MainFrame
import MainFrameButtonCommands
import Savable
import BciController


class MainWindow(MyWindows.TkWindow, Savable.Savable, Savable.Loadable):
    def __init__(self, connection):
        MyWindows.TkWindow.__init__(self, "VEP-BCI")
        self.connection = connection
        """ @type : connections.ConnectionProcessEnd.MainConnection """
        self.bottom_frame_buttons_states = ButtonsStateController.ButtonsStateController(self, (c.BOTTOM_FRAME,))
        self.training_tab_buttons_states = ButtonsStateController.ButtonsStateController(self, (c.MAIN_NOTEBOOK, c.TRAINING_TAB, c.TRAIN_FRAME))
        self.bci_controller = BciController.BciController(self, self.bottom_frame_buttons_states, c.BCI_MESSAGES)
        self.training_controller = BciController.BciController(self, self.training_tab_buttons_states, c.TRAINING_MESSAGES)
        button_commands = MainFrameButtonCommands.MainFrameButtonCommands(self, self.bci_controller, self.training_controller)
        self.main_frame = MainFrame.MainFrame(self, button_commands.commands)
        self.loadValuesAtStartup()
        self.bottom_frame_buttons_states.setInitialStates()
        self.training_tab_buttons_states.setInitialStates()
        self.checkMessages()
        self.mainloop()

    def checkMessages(self):
        message = self.connection.receiveMessageInstant()
        if self.bci_controller.canHandle(message):
            self.bci_controller.handle(message)
        elif self.training_controller.canHandle(message):
            self.training_controller.handle(message)
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
        self.training_tab_buttons_states.setInitialStates()
