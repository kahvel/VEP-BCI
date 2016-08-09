from messaging.gui_messaging import MessagingInterface, AbstractMessageSenders
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


class Classification(MessagingInterface.Classification, AbstractMessageSenders.NonLeaf):
    def __init__(self, widgets_list, connection):
        MessagingInterface.Classification.__init__(self)
        AbstractMessageSenders.NonLeaf.__init__(self, widgets_list)
        self.features = []
        self.classification_options = []
        self.classification_tab_parser = ClassificationParser.ClassificationParser()
        self.connection = connection

    def sendFeaturesToRootEvent(self, results):
        self.features.append(results)

    def sendClassificationOptionsToRootEvent(self, classification_options):
        self.classification_options = self.classification_tab_parser.parseData(classification_options)

    def resetFeatures(self):
        self.features = []

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


class GetDataHandler(AbstractMessageSenders.NonLeaf):
    def __init__(self, widgets_list, connection):
        AbstractMessageSenders.NonLeaf.__init__(self, widgets_list)
        self.connection = connection

    def getData(self, message):
        self.connection.sendMessage(message)
        return self.connection.receiveMessageBlock()


class TrialEndedHandler(MessagingInterface.TrialEndedHandler, GetDataHandler):
    def __init__(self, widgets_list, connection):
        MessagingInterface.TrialEndedHandler.__init__(self)
        GetDataHandler.__init__(self, widgets_list, connection)

    def trialEndedEvent(self):
        self.evokeResultsReceivedEvent()
        self.evokeNewResultsReceivedEvent()
        self.evokeRecordedEegReceivedEvent()
        self.evokeRecordedFeaturesReceivedEvent()
        self.evokeRecordedFrequenciesReceivedEvent()
        self.evokeAddNewRecordingTabEvent()  # Has to be last

    def evokeResultsReceivedEvent(self):
        results = self.getData(c.GET_RESULTS_MESSAGE)
        self.sendEventToChildren(lambda x: x.resultsReceivedEvent(results))

    def evokeNewResultsReceivedEvent(self):
        results = self.getData(c.GET_NEW_RESULTS_MESSAGE)
        self.sendEventToChildren(lambda x: x.newResultsReceivedEvent(results))

    def evokeRecordedEegReceivedEvent(self):
        results = self.getData(c.GET_RECORDED_EEG_MESSAGE)
        self.sendEventToChildren(lambda x: x.recordedEegReceivedEvent(results))

    def evokeRecordedFeaturesReceivedEvent(self):
        results = self.getData(c.GET_RECORDED_FEATURES_MESSAGE)
        self.sendEventToChildren(lambda x: x.recordedFeaturesReceivedEvent(results))

    def evokeRecordedFrequenciesReceivedEvent(self):
        results = self.getData(c.GET_RECORDED_FREQUENCIES_MESSAGE)
        self.sendEventToChildren(lambda x: x.recordedFrequenciesReceivedEvent(results))

    def evokeAddNewRecordingTabEvent(self):
        self.sendEventToChildren(lambda x: x.addNewRecordingTabEvent())


class TrainingEndedHandler(MessagingInterface.TrainingEndedHandler, GetDataHandler):
    def __init__(self, widgets_list, connection):
        MessagingInterface.TrainingEndedHandler.__init__(self)
        GetDataHandler.__init__(self, widgets_list, connection)

    def trainingEndedEvent(self):
        self.evokeModelReceivedEvent()
        self.evokeTrainingDataReceivedEvent()
        self.evokeTrainingLabelsReceivedEvent()
        self.evokeValidationDataReceivedEvent()
        self.evokeValidationLabelsReceivedEvent()
        self.evokeAddNewModelTabEvent()

    def evokeAddNewModelTabEvent(self):
        self.sendEventToChildren(lambda x: x.addNewModelTabEvent())

    def evokeModelReceivedEvent(self):
        model = self.getData(c.GET_MODEL_MESSAGE)
        self.sendEventToChildren(lambda x: x.modelReceivedEvent(model))

    def evokeValidationDataReceivedEvent(self):
        data = self.getData(c.GET_VALIDATION_DATA_MESSAGE)
        self.sendEventToChildren(lambda x: x.validationDataReceivedEvent(data))

    def evokeValidationLabelsReceivedEvent(self):
        labels = self.getData(c.GET_VALIDATION_LABELS_MESSAGE)
        self.sendEventToChildren(lambda x: x.validationLabelsReceivedEvent(labels))

    def evokeTrainingDataReceivedEvent(self):
        data = self.getData(c.GET_TRAINING_DATA_MESSAGE)
        self.sendEventToChildren(lambda x: x.trainingDataReceivedEvent(data))

    def evokeTrainingLabelsReceivedEvent(self):
        data = self.getData(c.GET_TRAINING_LABELS_MESSAGE)
        self.sendEventToChildren(lambda x: x.trainingLabelsReceivedEvent(data))


class MainWindowMessageHandler(Bci, Robot, Classification, TrialEndedHandler, TrainingEndedHandler, AbstractMessageSenders.Root, MessagingInterface.MessagingInterface):
    def __init__(self, connection, main_window_message_handler, main_frame, main_window, button_state_controller):
        Bci.__init__(self, main_window_message_handler, main_window, button_state_controller)
        Robot.__init__(self, connection)
        Classification.__init__(self, [main_frame], connection)
        TrialEndedHandler.__init__(self, [main_frame], connection)
        TrainingEndedHandler.__init__(self, [main_frame], connection)
        AbstractMessageSenders.Root.__init__(self, [main_frame], main_window_message_handler)
        MessagingInterface.MessagingInterface.__init__(self)
        self.main_frame = main_frame

    def checkPostOfficeMessages(self):
        message = self.connection.receiveMessageInstant()
        if self.main_window_message_handler.canHandle(message):
            self.main_window_message_handler.handle(message)
