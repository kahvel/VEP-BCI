import constants as c

import random


class TargetSwitcher(object):
    def __init__(self, connections):
        self.previous_target_change = 0
        self.target_duration_seconds = None
        self.target_duration_plus_minus = None
        self.allow_repeating = None
        self.test_target_option = None
        self.target_freqs = None
        self.connections = connections
        self.random_target_duration = None

    def setup(self, options):
        self.target_duration_seconds = options[c.DATA_TEST][c.TEST_TAB_TIME_PER_TARGET]
        self.target_duration_plus_minus = options[c.DATA_TEST][c.TEST_TAB_TIME_PER_TARGET_PLUS_MINUS]
        self.allow_repeating = options[c.DATA_TEST][c.TEST_TAB_ALLOW_REPEATING]
        self.test_target_option = options[c.DATA_TEST][c.TEST_TAB_TARGET_OPTION_MENU]
        self.target_freqs = options[c.DATA_FREQS]

    def resetPreviousTargetChange(self):
        self.previous_target_change = 0

    def getRandomNonRepeatingTarget(self, targets, previous_target):
        if previous_target is not None and len(targets) > 1:
            targets.remove(previous_target)
        return random.choice(targets)

    def getRandomTarget(self, targets, previous_target):
        if self.allow_repeating:
            return random.choice(targets)
        else:
            return self.getRandomNonRepeatingTarget(targets, previous_target)

    def getRecordingTarget(self, targets):
        """
        Makes sure that we get enough data for all targets when recording.
        If choosing completely randomly, we might not get enough data for some targets.
        :param targets:
        :return:
        """
        if self.recording_targets == []:
            self.recording_targets = targets
        return self.recording_targets.pop(random.randint(0, len(self.recording_targets)-1))

    def setRandomTargetDuration(self):
        if self.isTimed() or self.isRecording():
            self.random_target_duration = self.getRandomTargetDuration()

    def getTargetAccordingToType(self, previous_target):
        if self.isRandom() or self.isTimed():
            return self.getRandomTarget(self.target_freqs.keys(), previous_target)
        elif self.isRecording():
            return self.getRecordingTarget(self.target_freqs.keys())
        elif self.test_target_option != c.TEST_TARGET_NONE:
            return self.test_target_option
        else:
            return None

    def getNextTarget(self, previous_target):
        self.setRandomTargetDuration()
        return self.getTargetAccordingToType(previous_target)

    def isRandom(self):
        return self.test_target_option == c.TEST_TARGET_RANDOM

    def isTimed(self):
        return self.test_target_option == c.TEST_TARGET_TIMED

    def isRecording(self):
        return self.test_target_option == c.TEST_TARGET_RECORDING

    def handleTargetChanging(self, target):
        target = self.getNextTarget(target)
        if target is not None:
            self.connections.sendTargetMessage(target)
        return target

    def needNewTarget(self, target_identified, message_counter):
        if self.isRandom():
            return target_identified
        elif self.isTimed() or self.isRecording():
            return self.checkTimeExceeded(message_counter)
        else:
            return False

    def getRandomTargetDuration(self):
        return self.target_duration_seconds + random.randint(-self.target_duration_plus_minus, self.target_duration_plus_minus)

    def checkTimeExceeded(self, message_counter):
        if (message_counter - self.previous_target_change) / float(c.HEADSET_FREQ) >= self.random_target_duration:
            self.previous_target_change = message_counter
            return True
        else:
            return False
