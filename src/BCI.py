import constants as c

import Results
import TargetIdentification
import Standby

import random


class BCI(object):
    def __init__(self, connections, main_connection, recording):
        self.connections = connections
        self.main_connection = main_connection
        self.results = Results.Results()
        self.new_results = Results.Results()
        self.recording = recording
        self.standby = Standby.Standby()
        self.target_identification = TargetIdentification.TargetIdentification(self.connections, self.results, self.new_results, self.standby)
        self.message_counter = 0
        self.previous_target_change = 0
        self.target_duration_seconds = 9

    def setup(self, options):
        self.connections.setup(options)
        self.setRecording(options[c.DATA_RECORD][c.TRAINING_RECORD])
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
        self.target_identification.resetResults(options[c.DATA_FREQS].values())
        target_freqs = options[c.DATA_FREQS]
        self.results.start(target_freqs.values())
        self.new_results.start(target_freqs.values())
        self.recording.start(target_freqs)
        self.connections.sendMessage(c.START_MESSAGE)
        message = self.targetChangingLoop(
            options[c.DATA_TEST],
            target_freqs,
        )
        self.connections.sendMessage(c.STOP_MESSAGE)
        self.results.trialEnded(self.message_counter)
        self.new_results.trialEnded(self.message_counter)
        self.recording.trialEnded()
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
                self.recording.collectExpectedTarget(target, self.message_counter)
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
            self.recording.collectPacket(message)
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
        print self.message_counter - self.previous_target_change, current_target
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

    def setRecording(self, record_option):
        if record_option == c.TRAINING_RECORD_NORMAL:
            self.recording.enableNormal()
        elif record_option == c.TRAINING_RECORD_NEUTRAL:
            self.recording.enableNeutral()
        elif record_option == c.TRAINING_RECORD_DISABLED:
            self.recording.disableRecording()
        else:
            raise Exception("Recording option menu in invalid state!")

    def setupStandby(self, options):
        if self.standby.enabled:
            self.standby.setup(options[c.DATA_FREQS][options[c.DATA_TEST][c.TEST_STANDBY]])

    def resetResults(self):
        self.results.reset()
        self.new_results.reset()

    def getResults(self):
        return "\nNew:\n" + self.new_results.__repr__() + "Old:\n" + self.results.__repr__()

    def loadEeg(self, file_content):
        self.recording.loadEeg(file_content)

    def saveEeg(self):
        return self.recording.saveEeg()

    def resetRecording(self):
        self.recording.reset()
