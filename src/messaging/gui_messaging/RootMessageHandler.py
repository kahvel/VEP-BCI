from messaging.gui_messaging import MessagingInterface, AbstractMessageSenders
from parsers import ModelsParser
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


class Models(MessagingInterface.Models, AbstractMessageSenders.NonLeaf):
    def __init__(self, widgets_list, connection):
        MessagingInterface.Models.__init__(self)
        AbstractMessageSenders.NonLeaf.__init__(self, widgets_list)
        self.features = []
        self.eeg = []
        self.model_options = []
        self.model_tab_parser = ModelsParser.ModelsOptionsParser()
        self.connection = connection

    def sendFeaturesToRootEvent(self, results):
        self.features.append(results)

    def sendEegToRootEvent(self, results):
        self.eeg.append(results)

    def sendModelOptionsToRootEvent(self, classification_options):
        self.model_options = self.model_tab_parser.parseData(classification_options)

    def resetFeatures(self):
        self.features = []

    def resetEeg(self):
        self.eeg = []

    def sendFeatureRecrding(self):
        self.connection.sendMessage(c.SEND_RECORDED_FEATURES_MESSAGE)
        self.connection.sendMessage(self.features)

    def sendEegRecording(self):
        self.connection.sendMessage(c.SEND_RECORDED_EEG_MESSAGE)
        self.connection.sendMessage(self.eeg)

    def getFeatures(self):
        self.resetFeatures()
        self.sendEventToChildren(lambda x: x.getFeaturesEvent())
        return len(self.features) != 0

    def getEeg(self):
        self.resetEeg()
        self.sendEventToChildren(lambda x: x.getEegEvent())
        return len(self.eeg) != 0

    def sendClassificationOptions(self):
        self.sendEventToChildren(lambda x: x.getModelOptionsEvent())
        self.connection.sendMessage(c.SEND_CLASSIFICATION_OPTIONS)
        self.connection.sendMessage(self.model_options)

    def sendStartTraining(self):
        self.connection.sendMessage(c.TRAINING_START_MESSAGE)

    def sendDisableModelOptions(self):
        self.sendEventToChildren(lambda x: x.disableModelOptionsEvent())

    def trainButtonClickedEvent(self):
        if self.getFeatures() and self.getEeg():
            self.sendDisableModelOptions()
            self.sendEegRecording()
            self.sendFeatureRecrding()  # Has to be before sendClassificationOptions!
            self.sendClassificationOptions()
            self.sendStartTraining()
        else:
            print "Training Failed! No recordings selected!"


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

    def newRecordingCheckbuttonEvent(self):
        self.sendEventToChildren(lambda x: x.addNewRecordingCheckbuttonEvent())

    def newRecordingOptionEvent(self):
        self.sendEventToChildren(lambda x: x.addNewRecordingOptionEvent())

    def trialEndedEvent(self):
        self.evokeResultsReceivedEvent()
        self.evokeRecordedEegReceivedEvent()
        self.evokeRecordedFeaturesReceivedEvent()
        self.evokeRecordedFrequenciesReceivedEvent()
        self.newRecordingCheckbuttonEvent()
        self.newRecordingOptionEvent()
        self.evokeAddNewRecordingTabEvent()  # Has to be last

    def evokeResultsReceivedEvent(self):
        results = self.getData(c.GET_RESULTS_MESSAGE)
        self.sendEventToChildren(lambda x: x.resultsReceivedEvent(results))

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
        self.evokeSecondModelReceivedEvent()
        self.evokeTrainingDataReceivedEvent()
        self.evokeTrainingLabelsReceivedEvent()
        self.evokeValidationDataReceivedEvent()
        self.evokeValidationLabelsReceivedEvent()
        self.evokeThresholdsReceivedEvent()
        self.evokeMinMaxReceivedEvent()
        self.evokeTrainingRocReceivedEvent()
        self.evokeTestingRocReceivedEvent()
        self.evokeTrainingPrcReceivedEvent()
        self.evokeTestingPrcReceivedEvent()
        self.evokeUsedFeaturesReceivedEvent()
        self.evokeAddNewModelTabEvent()

    def evokeUsedFeaturesReceivedEvent(self):
        used_features = self.getData(c.GET_USED_FEATURES_MESSAGE)
        self.sendEventToChildren(lambda x: x.usedFeaturesReceivedEvent(used_features))

    def evokeAddNewModelTabEvent(self):
        self.sendEventToChildren(lambda x: x.addNewModelTabEvent())

    def evokeModelReceivedEvent(self):
        model = self.getData(c.GET_MODEL_MESSAGE)
        self.sendEventToChildren(lambda x: x.modelReceivedEvent(model))

    def evokeSecondModelReceivedEvent(self):
        model = self.getData(c.GET_SECOND_MODEL_MESSAGE)
        self.sendEventToChildren(lambda x: x.secondModelReceivedEvent(model))

    def evokeValidationDataReceivedEvent(self):
        data = self.getData(c.GET_TESTING_DATA_MESSAGE)
        self.sendEventToChildren(lambda x: x.testingDataReceivedEvent(data))

    def evokeValidationLabelsReceivedEvent(self):
        labels = self.getData(c.GET_TESTING_LABELS_MESSAGE)
        self.sendEventToChildren(lambda x: x.testingLabelsReceivedEvent(labels))

    def evokeTrainingDataReceivedEvent(self):
        data = self.getData(c.GET_TRAINING_DATA_MESSAGE)
        self.sendEventToChildren(lambda x: x.trainingDataReceivedEvent(data))

    def evokeTrainingLabelsReceivedEvent(self):
        data = self.getData(c.GET_TRAINING_LABELS_MESSAGE)
        self.sendEventToChildren(lambda x: x.trainingLabelsReceivedEvent(data))

    def evokeThresholdsReceivedEvent(self):
        thresholds = self.getData(c.GET_THRESHOLDS_MESSAGE)
        self.sendEventToChildren(lambda x: x.thresholdsReceivedEvent(thresholds))

    def evokeMinMaxReceivedEvent(self):
        min_max = self.getData(c.GET_MIN_MAX_MESSAGE)
        self.sendEventToChildren(lambda x: x.minMaxReceivedEvent(min_max))

    def evokeTrainingRocReceivedEvent(self):
        training_roc = self.getData(c.GET_TRAINING_ROC_MESSAGE)
        self.sendEventToChildren(lambda x: x.trainingRocReceivedEvent(training_roc))

    def evokeTestingRocReceivedEvent(self):
        validation_roc = self.getData(c.GET_TESTING_ROC_MESSAGE)
        self.sendEventToChildren(lambda x: x.testingRocReceivedEvent(validation_roc))

    def evokeTrainingPrcReceivedEvent(self):
        training_roc = self.getData(c.GET_TRAINING_PRC_MESSAGE)
        self.sendEventToChildren(lambda x: x.trainingPrcReceivedEvent(training_roc))

    def evokeTestingPrcReceivedEvent(self):
        validation_roc = self.getData(c.GET_TESTING_PRC_MESSAGE)
        self.sendEventToChildren(lambda x: x.testingPrcReceivedEvent(validation_roc))


class MainWindowMessageHandler(Bci, Robot, Models, TrialEndedHandler, TrainingEndedHandler, AbstractMessageSenders.Root, MessagingInterface.MessagingInterface):
    def __init__(self, connection, main_window_message_handler, main_frame, main_window, button_state_controller):
        Bci.__init__(self, main_window_message_handler, main_window, button_state_controller)
        Robot.__init__(self, connection)
        Models.__init__(self, [main_frame], connection)
        TrialEndedHandler.__init__(self, [main_frame], connection)
        TrainingEndedHandler.__init__(self, [main_frame], connection)
        AbstractMessageSenders.Root.__init__(self, [main_frame], main_window_message_handler)
        MessagingInterface.MessagingInterface.__init__(self)
        self.main_frame = main_frame

    def checkPostOfficeMessages(self):
        message = self.connection.receiveMessageInstant()
        if self.main_window_message_handler.canHandle(message):
            self.main_window_message_handler.handle(message)
