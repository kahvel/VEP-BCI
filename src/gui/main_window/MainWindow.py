from gui.main_window import MainFrame
from gui import AbstractMainWindow
import PostOfficeMessageHandler
from parsers import InputParser
import constants as c


class MainWindow(AbstractMainWindow.AbstractMainWindow):
    def __init__(self, connection):
        AbstractMainWindow.AbstractMainWindow.__init__(self, connection, c.DEFAULT_SETTINGS_FILE_NAME)

    def getMainFrame(self):
        return MainFrame.MainFrame(self)

    def getMessageHandler(self, main_frame, bottom_frame_buttons_states, connection):
        input_parser = InputParser.MainInputParser()
        return PostOfficeMessageHandler.PostOfficeMessageHandler(main_frame, bottom_frame_buttons_states, input_parser, connection)
