import random

import constants as c
import Results
import TargetIdentification
import Standby
import Recording
from parsers import FeaturesParser


class BCI(object):
    def __init__(self, connections):
        self.connections = connections
        self.results = None
        self.new_results = None
        self.recording = None
        self.standby = Standby.Standby()
        self.target_identification = TargetIdentification.TargetIdentification(self.connections, self.results, self.new_results, self.standby)
        self.message_counter = 0
        self.previous_target_change = 0
        self.target_duration_seconds = 9
        self.record_option = None
        self.allow_repeating = None
        self.test_target_option = None
        self.total_time = None
        self.target_freqs = None
        self.flattener = FeaturesParser.Flattener()
        self.setup_succeeded = False
        self.exit_flag = False

    def flattenFeatureVector(self, feature_vector):
        return self.flattener.parseFeatures(feature_vector)

    def setup(self, options):
        self.setup_succeeded = False
        self.record_option = options[c.DATA_RECORD][c.TRAINING_RECORD]
        self.allow_repeating = options[c.DATA_TEST][c.TEST_TAB_ALLOW_REPEATING]
        self.test_target_option = options[c.DATA_TEST][c.TEST_TAB_TARGET]
        self.total_time = self.getTotalTime(options[c.DATA_TEST][c.TEST_TAB_UNLIMITED], options[c.DATA_TEST][c.TEST_TAB_TIME])
        self.target_freqs = options[c.DATA_FREQS]
        self.setStandbyState(options[c.DATA_TEST][c.TEST_TAB_STANDBY])
        self.setupStandby(options)
        self.target_identification.setup(options)
        self.setup_succeeded = True

    def setupSucceeded(self):
        return self.setup_succeeded

    def setExitFlag(self, value):
        self.exit_flag = value

    def start(self):
        self.exit_flag = False
        self.message_counter = 0
        self.previous_target_change = 0
        self.target_identification.resetResults(self.target_freqs.values())
        self.results = Results.Result(self.target_freqs)
        self.new_results = Results.Result(self.target_freqs)
        self.recording = Recording.Recording(self.target_freqs, self.record_option)
        self.connections.sendMessage(c.START_MESSAGE)
        self.targetChangingLoop()
        self.connections.sendMessage(c.STOP_MESSAGE)
        self.results.setTime(self.message_counter)
        self.new_results.setTime(self.message_counter)

    def getTotalTime(self, unlimited, test_time):
        return float("inf") if unlimited else test_time

    def getRandomNonRepeatingTarget(self, targets, previous_target):
        if previous_target is not None and len(targets) > 1:
            targets.remove(previous_target)
        return random.choice(targets)

    def getRandomTarget(self, targets, previous_target):
        if self.allow_repeating:
            return random.choice(targets)
        else:
            return self.getRandomNonRepeatingTarget(targets, previous_target)

    def getNextTarget(self, previous_target):
        if self.isRandom() or self.isTimed():
            return self.getRandomTarget(self.target_freqs.keys(), previous_target)
        elif self.test_target_option != c.TEST_TARGET_NONE:
            return self.test_target_option
        else:
            return None

    def isRandom(self):
        return self.test_target_option == c.TEST_TARGET_RANDOM

    def isTimed(self):
        return self.test_target_option == c.TEST_TARGET_TIMED

    def handleTargetChanging(self, target):
        target = self.getNextTarget(target)
        if target is not None:
            self.connections.sendTargetMessage(target)
        return target

    def targetChangingLoop(self):
        target = None
        while self.message_counter < self.total_time and not self.exit_flag:
            target = self.handleTargetChanging(target)
            self.target_identification.resetTargetVariables()
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
            features = self.flattenFeatureVector(features)  # Use only with new target identification
            self.recording.collectFeatures(features, current_target, self.message_counter)
            predicted_target = self.target_identification.handleFreqMessages(features, self.target_freqs, current_target)
            self.recording.addPredictionToFeatures(predicted_target)
        self.recording.addPredictionToEeg(predicted_target)

    def getNextPacket(self):
        return self.connections.receiveEmotivMessage()

    def handleVideoStreamMessages(self):
        message = self.connections.receiveRobotMessage()
        if message is not None:
            self.connections.sendTargetMessage(message)

    def checkTimeExceeded(self):
        if (self.message_counter - self.previous_target_change) / c.HEADSET_FREQ > self.target_duration_seconds + random.randint(-2, 2):
            self.previous_target_change = self.message_counter
            return True
        else:
            return False

    def needNewTarget(self):
        if self.isRandom():
            return self.target_identification.need_new_target
        elif self.isTimed():
            return self.checkTimeExceeded()
        else:
            return False

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
