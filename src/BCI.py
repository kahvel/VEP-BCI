import constants as c

import Results
import TargetIdentification
import Standby
import Recording

import random


class BCI(object):
    def __init__(self, connections, main_connection):
        self.connections = connections
        self.main_connection = main_connection
        self.results = None
        self.new_results = None
        self.recording = None
        self.standby = Standby.Standby()
        self.target_identification = TargetIdentification.TargetIdentification(self.connections, self.results, self.new_results, self.standby)
        self.message_counter = 0
        self.previous_target_change = 0
        self.target_duration_seconds = 9
        self.record_option = None

    def setup(self, options):
        self.connections.setup(options)
        self.record_option = options[c.DATA_RECORD][c.TRAINING_RECORD]
        self.setStandby(options)
        self.setupStandby(options)
        if self.connections.setupSuccessful():
            self.target_identification.setup(options)
            return c.SUCCESS_MESSAGE
        else:
            return c.FAIL_MESSAGE

    def start(self, options):
        self.message_counter = 0
        self.previous_target_change = 0
        target_freqs = options[c.DATA_FREQS]
        self.target_identification.resetResults(target_freqs.values())
        self.results = Results.Result(target_freqs)
        self.new_results = Results.Result(target_freqs)
        self.recording = Recording.Recording(target_freqs, self.record_option)
        self.connections.sendMessage(c.START_MESSAGE)
        message = self.targetChangingLoop(
            options[c.DATA_TEST],
            target_freqs,
        )
        self.connections.sendMessage(c.STOP_MESSAGE)
        self.results.setTime(self.message_counter)
        self.new_results.setTime(self.message_counter)
        return message

    def getTotalTime(self, unlimited, test_time):
        return float("inf") if unlimited else test_time

    def getTarget(self, test_target_option, target_freqs, previous_target):
        if self.isRandom(test_target_option) or self.isTimed(test_target_option):
            targets = target_freqs.keys()
            if previous_target is not None and len(targets) > 1:
                targets.remove(previous_target)
            return random.choice(targets)
        elif test_target_option != c.TEST_NONE:
            return test_target_option
        else:
            return None

    def isRandom(self, test_target_option):
        return test_target_option == c.TEST_RANDOM

    def isTimed(self, test_target_option):
        return test_target_option == c.TEST_TIMED

    def targetChangingLoop(self, options, target_freqs):
        total_time = self.getTotalTime(options[c.TEST_UNLIMITED], options[c.TEST_TIME])
        target = None
        while self.message_counter < total_time:
            target = self.getTarget(options[c.TEST_TARGET], target_freqs, target)
            if target is not None:
                self.connections.sendTargetMessage(target)
            self.target_identification.resetTargetVariables()
            message = self.startPacketSending(target_freqs, target, total_time, options[c.TEST_TARGET])
            if message is not None:
                return message
        self.main_connection.sendMessage(c.STOP_MESSAGE)
        return c.STOP_MESSAGE

    def handleEmotivMessages(self, target_freqs, current_target):
        message = self.getNextPacket()
        if message is not None:
            self.message_counter += 1
            self.recording.collectPacket(message, current_target)
            self.connections.sendExtractionMessage(message)
            self.connections.sendPlotMessage(message)
            self.handleExtractionMessages(target_freqs, current_target)

    def handleExtractionMessages(self, target_freqs, current_target):
        self.target_identification.handleFreqMessages(
            self.connections.receiveExtractionMessage(),
            target_freqs,
            current_target
        )

    def getNextPacket(self):
        return self.connections.receiveEmotivMessage()

    def handleRobotMessages(self):
        message = self.connections.receiveRobotMessage()
        if message is not None:
            self.connections.sendTargetMessage(message)

    def checkTimeExceeded(self):
        if (self.message_counter - self.previous_target_change) / c.HEADSET_FREQ > self.target_duration_seconds + random.randint(-2, 2):
            self.previous_target_change = self.message_counter
            return True
        else:
            return False

    def needNewTarget(self, test_target_option):
        if self.isRandom(test_target_option):
            return self.target_identification.need_new_target
        elif self.isTimed(test_target_option):
            return self.checkTimeExceeded()
        else:
            return False

    def startPacketSending(self, target_freqs, current_target, total_time, test_target_option):
        while not self.needNewTarget(test_target_option) and self.message_counter < total_time:
            main_message = self.main_connection.receiveMessageInstant()
            if main_message in c.ROBOT_COMMANDS:
                self.connections.sendRobotMessage(main_message)
            elif main_message is not None:
                return main_message
            self.handleEmotivMessages(target_freqs, current_target)
            self.handleRobotMessages()

    def setStandby(self, options):
        if options[c.DATA_TEST][c.TEST_STANDBY] == c.TEST_NONE:
            self.standby.disable()
        else:
            self.standby.enable()

    def setupStandby(self, options):
        if self.standby.enabled:
            self.standby.setup(options[c.DATA_FREQS][options[c.DATA_TEST][c.TEST_STANDBY]])

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
