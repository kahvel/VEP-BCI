from bci import DataIterator
import constants as c

import random


class AbstractTargetSwitcher(object):
    def __init__(self):
        pass

    def resetPreviousTargetChangeAndRecordingTargets(self):
        raise NotImplementedError("resetPreviousTargetChangeAndRecordingTargets not implemented!")

    def handleTargetChanging(self, target):
        raise NotImplementedError("handleTargetChanging not implemented!")

    def needNewTarget(self, target_identified, message_counter):
        raise NotImplementedError("needNewTarget not implemented!")


class TargetSwitcher(AbstractTargetSwitcher):
    def __init__(self, connections):
        AbstractTargetSwitcher.__init__(self)
        self.previous_target_change = 0
        self.target_duration_seconds = None
        self.target_duration_plus_minus = None
        self.allow_repeating = None
        self.test_target_option = None
        self.target_freqs = None
        self.connections = connections
        self.random_target_duration = None
        self.recently_not_used_targets = []

    def setup(self, options):
        self.target_duration_seconds = options[c.DATA_TEST][c.TEST_TAB_TIME_PER_TARGET]
        self.target_duration_plus_minus = options[c.DATA_TEST][c.TEST_TAB_TIME_PER_TARGET_PLUS_MINUS]
        self.allow_repeating = options[c.DATA_TEST][c.TEST_TAB_ALLOW_REPEATING]
        self.test_target_option = options[c.DATA_TEST][c.TEST_TAB_TARGET_OPTION_MENU]
        self.target_freqs = options[c.DATA_FREQS]
        self.recently_not_used_targets = []

    def resetPreviousTargetChangeAndRecordingTargets(self):
        self.previous_target_change = 0
        self.recently_not_used_targets = []

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
        if self.recently_not_used_targets == []:
            self.recently_not_used_targets = targets
        return self.recently_not_used_targets.pop(random.randint(0, len(self.recently_not_used_targets)-1))

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


class RecordedTargetSwitcher(AbstractTargetSwitcher, DataIterator.AbstractDataIterator):
    def __init__(self, bci):
        AbstractTargetSwitcher.__init__(self)
        DataIterator.AbstractDataIterator.__init__(self, bci)
        self.eeg_or_features_option = None
        self.recording = None

    def setup(self, options):
        self.eeg_or_features_option = options[c.DATA_TEST][c.TEST_TAB_RECORDED_TYPE_OPTION_MENU]
        if self.eeg_or_features_option == c.TEST_RECORDED_TYPE_EEG:
            self.recording = options[c.DATA_RECORD][c.RECORDING_TAB_RECORDING_DATA][c.RECORDING_TAB_EEG].getExpectedTargets()
        elif self.eeg_or_features_option == c.TEST_RECORDED_TYPE_FEATURES:
            self.recording = options[c.DATA_RECORD][c.RECORDING_TAB_RECORDING_DATA][c.RECORDING_TAB_FEATURES].getExpectedTargets()
        self.setupIndexAndLength(len(self.recording))

    def resetPreviousTargetChangeAndRecordingTargets(self):
        pass

    def handleTargetChanging(self, target):
        return self.recording[self.getIndexAndIncrease()]

    def needNewTarget(self, target_identified, message_counter):
        return True
