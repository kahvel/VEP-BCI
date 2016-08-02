import MessagingInterface
import constants as c


class Bci(MessagingInterface.Bci):
    def __init__(self, post_office_message_handler, main_window, button_state_controller):
        MessagingInterface.Bci.__init__(self)
        self.button_state_controller = button_state_controller
        self.post_office_message_handler = post_office_message_handler
        self.main_window = main_window

    def startBciEvent(self):
        self.post_office_message_handler.start()

    def stopBciEvent(self):
        self.post_office_message_handler.stop()

    def setupBciEvent(self):
        self.post_office_message_handler.setup()

    def saveBciEvent(self):
        self.main_window.askSaveFile()

    def loadBciEvent(self):
        self.main_window.askLoadFile()
        self.button_state_controller.setInitialStates()

    def exitBciEvent(self):
        self.main_window.exit()


class Recording(MessagingInterface.Recording):
    def __init__(self, connection):
        MessagingInterface.Recording.__init__(self)
        self.connection = connection

    def saveEegEvent(self, file):
        self.connection.sendMessage(c.SAVE_EEG_MESSAGE)
        self.connection.sendMessage(file)

    def loadEegEvent(self, file):
        self.connection.sendMessage(c.LOAD_EEG_MESSAGE)
        self.connection.sendMessage(file)

    def resetEegEvent(self):
        self.connection.sendMessage(c.RESET_EEG_MESSAGE)


class Results(MessagingInterface.Results):
    def __init__(self, connection):
        MessagingInterface.Results.__init__(self)
        self.connection = connection

    def saveResultsEvent(self):
        self.connection.sendMessage(c.SAVE_RESULTS_MESSAGE)
        self.connection.sendMessage(file)

    def showResultsEvent(self):
        self.connection.sendMessage(c.SHOW_RESULTS_MESSAGE)

    def resetResultsEvent(self):
        self.connection.sendMessage(c.RESET_RESULTS_MESSAGE)


class Robot(MessagingInterface.Robot):
    def __init__(self, connection):
        MessagingInterface.Robot.__init__(self)
        self.connection = connection

    def robotForwardEvent(self):
        self.connection.sendMessage(c.MOVE_FORWARD)

    def robotBackwardEvent(self):
        self.connection.sendMessage(c.MOVE_BACKWARD)

    def robotLeftEvent(self):
        self.connection.sendMessage(c.MOVE_LEFT)

    def robotRightEvent(self):
        self.connection.sendMessage(c.MOVE_RIGHT)

    def robotStopEvent(self):
        self.connection.sendMessage(c.MOVE_STOP)



class MainWindowMessageHandler(Bci, Recording, Results, Robot):
    def __init__(self, connection, post_office_message_handler, main_frame, main_window, button_state_controller):
        Bci.__init__(self, post_office_message_handler, main_window, button_state_controller)
        Recording.__init__(self, connection)
        Results.__init__(self, connection)
        Robot.__init__(self, connection)
        self.main_frame = main_frame

    def bciIsStopped(self):
        return self.post_office_message_handler.isStopped()

    def checkPostOfficeMessages(self):
        message = self.connection.receiveMessageInstant()
        if self.post_office_message_handler.canHandle(message):
            self.post_office_message_handler.handle(message)

    def sendEventToRoot(self, function, needs_stopped_state=False):
        if needs_stopped_state and self.bciIsStopped() or not needs_stopped_state:
            function(self)
            function(self.main_frame)

    def targetAdded(self): pass

    def targetRemoved(self, deleted_tab): pass

    def targetDisabled(self, tabs, current_tab): pass

    def targetEnabled(self, tabs, current_tab): pass

    def trialEnded(self): pass
