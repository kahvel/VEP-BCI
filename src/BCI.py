from parsers import FeaturesParser
from target_identification import TargetIdentification
import constants as c
import Results
import Standby
import Recording
import TargetSwitcher


class BCI(object):
    def __init__(self, connections):
        self.connections = connections
        self.results = None
        self.new_results = None
        self.recording = None
        self.standby = Standby.Standby()
        self.target_identification = TargetIdentification.TargetIdentification(self.connections, self.standby)
        self.message_counter = 0
        self.record_option = None
        self.total_time = None
        self.target_freqs = None
        self.flattener = FeaturesParser.Flattener()
        self.setup_succeeded = True
        self.exit_flag = False
        self.target_switcher = TargetSwitcher.TargetSwitcher(self.connections)

    def flattenFeatureVector(self, feature_vector):
        return self.flattener.parseFeatures(feature_vector)

    def setup(self, options):
        self.setup_succeeded = True
        self.target_switcher.setup(options)
        self.record_option = options[c.DATA_RECORD][c.TRAINING_RECORD]
        self.total_time = self.getTotalTime(options[c.DATA_TEST][c.TEST_TAB_UNLIMITED], options[c.DATA_TEST][c.TEST_TAB_TOTAL_TIME])
        self.target_freqs = options[c.DATA_FREQS]
        self.setStandbyState(options[c.DATA_TEST][c.TEST_TAB_STANDBY])
        self.setupStandby(options)
        self.target_identification.setup(options)

    def setupSucceeded(self):
        return self.setup_succeeded and self.target_identification.setupSucceeded()

    def setExitFlag(self, value):
        self.exit_flag = value

    def start(self):
        self.exit_flag = False
        self.message_counter = 0
        self.target_switcher.resetPreviousTargetChangeAndRecordingTargets()
        self.target_identification.resetPrevResults(self.target_freqs.values())
        self.results = Results.Result(self.target_freqs)
        self.new_results = Results.Result(self.target_freqs)
        self.target_identification.setResults(self.results, self.new_results)
        self.recording = Recording.Recording(self.target_freqs, self.record_option)
        self.connections.sendMessage(c.START_MESSAGE)
        self.targetChangingLoop()
        self.results.setTime(self.message_counter)
        self.new_results.setTime(self.message_counter)
        self.connections.sendMessage(c.STOP_MESSAGE)

    def getTotalTime(self, unlimited, test_time):
        return float("inf") if unlimited else test_time

    def targetChangingLoop(self):
        target = None
        while self.message_counter < self.total_time and not self.exit_flag:
            target = self.target_switcher.handleTargetChanging(target)
            self.target_identification.resetNeedNewTarget()
            self.startPacketSending(target)

    def handleEmotivMessages(self, current_target):
        message = self.getNextPacket()
        if message is not None:
            self.message_counter += 1
            self.recording.collectPacket(message, current_target, self.message_counter)
            self.connections.sendExtractionMessage(message)
            self.connections.sendPlotMessage(message)
            self.handleExtractionMessages(current_target)

    def getFeatures(self):
        return self.connections.receiveExtractionMessage()

    def handleExtractionMessages(self, current_target):
        features = self.getFeatures()
        predicted_target = None
        if features is not None:
            flat_features = self.flattenFeatureVector(features)  # Use only with new target identification
            self.recording.collectFeatures(flat_features, current_target, self.message_counter)
            predicted_target = self.target_identification.handleFreqMessages(flat_features, features, self.target_freqs, current_target)
            self.recording.addPredictionToFeatures(predicted_target)
        self.recording.addPredictionToEeg(predicted_target)

    def getNextPacket(self):
        return self.connections.receiveEmotivMessage()

    def handleVideoStreamMessages(self):
        message = self.connections.receiveRobotMessage()
        if message is not None:
            self.connections.sendTargetMessage(message)

    def needNewTarget(self):
        return self.target_switcher.needNewTarget(self.target_identification.need_new_target, self.message_counter)

    def startPacketSending(self, current_target):
        while not self.needNewTarget() and self.message_counter < self.total_time and not self.exit_flag:
            self.handleEmotivMessages(current_target)
            self.handleVideoStreamMessages()

    def setStandbyState(self, option):
        if option == c.TEST_TARGET_NONE:
            self.standby.disable()
        else:
            self.standby.enable()

    def setupStandby(self, options):
        if self.standby.enabled:
            self.standby.setup(options[c.DATA_FREQS][options[c.DATA_TEST][c.TEST_TAB_STANDBY]])

    def getResults(self):
        return self.results.getData()

    def getNewResults(self):
        return self.new_results.getData()

    def getRecordedEeg(self):
        return self.recording.getEeg()

    def getRecordedFeatures(self):
        return self.recording.getFeatures()

    def getRecordedFrequencies(self):
        return self.recording.getFrequencies()
