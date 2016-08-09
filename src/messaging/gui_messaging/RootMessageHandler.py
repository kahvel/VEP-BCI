from messaging.gui_messaging import MessagingInterface
from parsers import ClassificationParser
import constants as c


class Bci(MessagingInterface.Bci):
    def __init__(self, main_window_message_handler, main_window, button_state_controller):
        MessagingInterface.Bci.__init__(self)
        self.button_state_controller = button_state_controller
        self.main_window_message_handler = main_window_message_handler
        self.main_window = main_window

    def startButtonClickedEvent(self):
        self.main_window_message_handler.start()

    def stopButtonClickedEvent(self):
        self.main_window_message_handler.stop()

    def setupButtonClickedEvent(self):
        self.main_window_message_handler.setup()

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
        self.classification_options = []
        self.classification_tab_parser = ClassificationParser.ClassificationParser()

    def sendFeaturesToRootEvent(self, results):
        self.features.append(results)

    def sendClassificationOptionsToRootEvent(self, classification_options):
        self.classification_options = self.classification_tab_parser.parseData(classification_options)

    def resetFeatures(self):
        self.features = []


class MainWindowMessageHandler(Bci, MessagingInterface.Recording, MessagingInterface.Results, Robot, MessagingInterface.Root, MessagingInterface.Targets, Classification, MessagingInterface.Training):
    def __init__(self, connection, main_window_message_handler, main_frame, main_window, button_state_controller):
        Bci.__init__(self, main_window_message_handler, main_window, button_state_controller)
        MessagingInterface.Recording.__init__(self)
        MessagingInterface.Results.__init__(self)
        Robot.__init__(self, connection)
        MessagingInterface.Root.__init__(self, [main_frame], main_window_message_handler)
        MessagingInterface.Targets.__init__(self)
        Classification.__init__(self)
        MessagingInterface.Training.__init__(self)
        self.main_frame = main_frame

    def checkPostOfficeMessages(self):
        message = self.connection.receiveMessageInstant()
        if self.main_window_message_handler.canHandle(message):
            self.main_window_message_handler.handle(message)

    def trainingEndedEvent(self):
        self.evokeModelReceivedEvent()
        self.evokeAddNewModelTabEvent()

    def evokeAddNewModelTabEvent(self):
        self.sendEventToChildren(lambda x: x.addNewModelTabEvent())

    def evokeModelReceivedEvent(self):
        model = self.getResults(c.GET_MODEL_MESSAGE)
        self.sendEventToChildren(lambda x: x.modelReceivedEvent(model))

    def trialEndedEvent(self):
        self.evokeResultsReceivedEvent()
        self.evokeNewResultsReceivedEvent()
        self.evokeRecordedEegReceivedEvent()
        self.evokeRecordedFeaturesReceivedEvent()
        self.evokeRecordedFrequenciesReceivedEvent()
        self.evokeAddNewRecordingTabEvent()  # Has to be last

    def evokeAddNewRecordingTabEvent(self):
        self.sendEventToChildren(lambda x: x.addNewRecordingTabEvent())

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
        results = self.getResults(c.GET_RECORDED_EEG_MESSAGE)
        self.sendEventToChildren(lambda x: x.recordedEegReceivedEvent(results))

    def evokeRecordedFeaturesReceivedEvent(self):
        results = self.getResults(c.GET_RECORDED_FEATURES_MESSAGE)
        self.sendEventToChildren(lambda x: x.recordedFeaturesReceivedEvent(results))

    def evokeRecordedFrequenciesReceivedEvent(self):
        results = self.getResults(c.GET_RECORDED_FREQUENCIES_MESSAGE)
        self.sendEventToChildren(lambda x: x.recordedFrequenciesReceivedEvent(results))

    def sendFeatureRecrding(self):
        self.resetFeatures()
        self.sendEventToChildren(lambda x: x.getFeaturesEvent())
        self.connection.sendMessage(c.SEND_RECORDED_FEATURES_MESSAGE)
        self.connection.sendMessage(self.features)

    def sendClassificationOptions(self):
        self.sendEventToChildren(lambda x: x.getClassificationOptionsEvent())
        self.connection.sendMessage(c.SEND_CLASSIFICATION_OPTIONS)
        self.connection.sendMessage(self.classification_options)

    def sendStartTraining(self):
        self.connection.sendMessage(c.TRAINING_START_MESSAGE)

    def trainButtonClickedEvent(self):
        self.sendFeatureRecrding()
        self.sendClassificationOptions()
        self.sendStartTraining()
