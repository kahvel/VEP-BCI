from gui_messaging import MessagingInterface
import constants as c


class Bci(MessagingInterface.Bci):
    def __init__(self, post_office_message_handler, main_window, button_state_controller):
        MessagingInterface.Bci.__init__(self)
        self.button_state_controller = button_state_controller
        self.post_office_message_handler = post_office_message_handler
        self.main_window = main_window

    def startButtonClickedEvent(self):
        self.post_office_message_handler.start()

    def stopButtonClickedEvent(self):
        self.post_office_message_handler.stop()

    def setupButtonClickedEvent(self):
        self.post_office_message_handler.setup()

    def saveButtonClickedEvent(self):
        self.main_window.askSaveFile()

    def loadButtonClickedEvent(self):
        self.main_window.askLoadFile()
        self.button_state_controller.setInitialStates()

    def exitButtonClickedEvent(self):
        self.main_window.exit()


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


class Classification(MessagingInterface.Classification):
    def __init__(self):
        MessagingInterface.Classification.__init__(self)
        self.features = []

    def sendRecordingToRootEvent(self, results):
        self.features.append(results)

    def resetFeatures(self):
        self.features = []


class MainWindowMessageHandler(Bci, MessagingInterface.Recording, MessagingInterface.Results, Robot, MessagingInterface.Root, MessagingInterface.Targets, Classification):
    def __init__(self, connection, post_office_message_handler, main_frame, main_window, button_state_controller):
        Bci.__init__(self, post_office_message_handler, main_window, button_state_controller)
        MessagingInterface.Recording.__init__(self)
        MessagingInterface.Results.__init__(self)
        Robot.__init__(self, connection)
        MessagingInterface.Root.__init__(self, [main_frame], post_office_message_handler)
        MessagingInterface.Targets.__init__(self)
        Classification.__init__(self)
        self.main_frame = main_frame

    def checkPostOfficeMessages(self):
        message = self.connection.receiveMessageInstant()
        if self.post_office_message_handler.canHandle(message):
            self.post_office_message_handler.handle(message)

    def trialEndedEvent(self):
        self.evokeResultsReceivedEvent()
        self.evokeNewResultsReceivedEvent()
        self.evokeRecordedEegReceivedEvent()
        self.evokeRecordedFeaturesReceivedEvent()
        self.evokeRecordedFrequenciesReceivedEvent()

    def getResults(self, message):
        self.connection.sendMessage(message)
        return self.connection.receiveMessageBlock()

    def evokeResultsReceivedEvent(self):
        results = self.getResults(c.GET_RESULTS_MESSAGE)
        self.sendEventToChildren(lambda x: x.resultsReceivedEvent(results))

    def evokeNewResultsReceivedEvent(self):
        results = self.getResults(c.GET_NEW_RESULTS_MESSAGE)
        self.sendEventToChildren(lambda x: x.newResultsReceivedEvent(results))

    def evokeRecordedEegReceivedEvent(self):
        results = self.getResults(c.GET_RECORDED_EEG)
        self.sendEventToChildren(lambda x: x.recordedEegReceivedEvent(results))

    def evokeRecordedFeaturesReceivedEvent(self):
        results = self.getResults(c.GET_RECORDED_FEATURES)
        self.sendEventToChildren(lambda x: x.recordedFeaturesReceivedEvent(results))

    def evokeRecordedFrequenciesReceivedEvent(self):
        results = self.getResults(c.GET_RECORDED_FREQUENCIES)
        self.sendEventToChildren(lambda x: x.recordedFrequenciesReceivedEvent(results))

    def trainButtonClickedEvent(self):
        self.resetFeatures()
        self.sendEventToChildren(lambda x: x.getFeaturesEvent())
        # self.connection.sendMessage(self.features)
