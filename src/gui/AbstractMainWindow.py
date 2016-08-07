from gui import ButtonsStateController
from gui_messaging import RootMessageHandler
from gui_elements.windows import MyWindows
import Savable
import constants as c

import os


class AbstractMainWindow(MyWindows.TkWindow, Savable.Savable, Savable.Loadable):
    def __init__(self, connection, default_settings_file_name):
        MyWindows.TkWindow.__init__(self, "VEP-BCI")
        Savable.Savable.__init__(self)
        Savable.Loadable.__init__(self)
        self.connection = connection
        self.main_frame = self.getMainFrame()
        button_state_controller = ButtonsStateController.ButtonsStateController(self.main_frame, (c.BOTTOM_FRAME,))
        self.message_handler = RootMessageHandler.MainWindowMessageHandler(
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
            file = self.getDefaultSettingsFile()
            self.sendEventToAll(lambda x: x.loadBciSettingsEvent(file))
        except IOError:
            self.main_frame.loadDefaultValue()

    def exit(self):
        self.exitFlag = True
        self.connection.sendExitMessage()
        self.connection.close()
        self.destroy()
        print("Exited main window")

    def saveToFile(self, file):
        self.sendEventToAll(lambda x: x.saveBciSettingsEvent(file))

    def loadFromFile(self, file):
        self.sendEventToAll(lambda x: x.loadBciSettingsEvent(file))

    def sendEventToRoot(self, function, needs_stopped_state=False):
        self.message_handler.sendEventToRoot(function, needs_stopped_state)

    def sendEventToAll(self, function, needs_stopped_state=False):
        self.message_handler.sendEventToAll(function, needs_stopped_state)
