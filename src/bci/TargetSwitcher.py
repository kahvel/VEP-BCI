from bci import DataIterator
import constants as c

import random


class AbstractTargetSwitcher(object):
    def __init__(self, connections):
        self.connections = connections

    def resetPreviousTargetChangeAndRecordingTargets(self):
        raise NotImplementedError("resetPreviousTargetChangeAndRecordingTargets not implemented!")

    def handleTargetChanging(self, target):
        raise NotImplementedError("handleTargetChanging not implemented!")

    def needNewTarget(self, message_counter):
        raise NotImplementedError("needNewTarget not implemented!")

    def targetDetected(self):
        raise NotImplementedError("targetDetected not implemented!")


class TargetSwitcher(AbstractTargetSwitcher):
    def __init__(self, connections):
        AbstractTargetSwitcher.__init__(self, connections)
        self.previous_target_change = 0
        self.target_duration_seconds = None
        self.target_duration_plus_minus = None
        self.allow_repeating = None
        self.test_target_option = None
        self.target_freqs = None
        self.random_target_duration = None
        self.recently_not_used_targets = []
        self.need_new_target = None

    def setup(self, options):
        self.target_duration_seconds = options[c.DATA_TEST][c.TEST_TAB_TIME_PER_TARGET]
        self.target_duration_plus_minus = options[c.DATA_TEST][c.TEST_TAB_TIME_PER_TARGET_PLUS_MINUS]
        self.allow_repeating = options[c.DATA_TEST][c.TEST_TAB_ALLOW_REPEATING]
        self.test_target_option = options[c.DATA_TEST][c.TEST_TAB_TARGET_OPTION_MENU]
        self.target_freqs = options[c.DATA_FREQS]
        self.recently_not_used_targets = []
        self.need_new_target = True

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

    def getRecordingNonRepeatingTarget(self, recently_not_used_targets, previous_target):
        targets = recently_not_used_targets[:]
        targets.remove(previous_target)
        target = random.choice(targets)
        recently_not_used_targets.remove(target)
        return target

    def getRecordingTarget(self, targets, previous_target):
        """
        Makes sure that we get enough data for all targets when recording.
        If choosing completely randomly, we might not get enough data for some targets.
        :param targets:
        :return:
        """
        if self.recently_not_used_targets == []:
            self.recently_not_used_targets = targets
        if self.allow_repeating or not self.allow_repeating and previous_target not in self.recently_not_used_targets:
            return self.recently_not_used_targets.pop(random.randint(0, len(self.recently_not_used_targets)-1))
        else:
            return self.getRecordingNonRepeatingTarget(self.recently_not_used_targets, previous_target)

    def setRandomTargetDuration(self):
        if self.isTimed() or self.isRecording():
            self.random_target_duration = self.getRandomTargetDuration()

    def getTargetAccordingToType(self, previous_target):
        if self.isRandom() or self.isTimed():
            return self.getRandomTarget(self.target_freqs.keys(), previous_target)
        elif self.isRecording():
            return self.getRecordingTarget(self.target_freqs.keys(), previous_target)
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
        self.need_new_target = False
        return target

    def needNewTarget(self, message_counter):
        if self.isRandom():
            return self.need_new_target
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

    def targetDetected(self):
        self.need_new_target = True


class RecordedTargetSwitcher(AbstractTargetSwitcher, DataIterator.AbstractDataIterator):
    def __init__(self, bci, connections):
        AbstractTargetSwitcher.__init__(self, connections)
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

    def handleTargetChanging(self, previous_target):
        target = self.recording[self.getIndexAndIncrease()]
        if target != previous_target:
            self.connections.sendTargetMessage(target)
        return target

    def needNewTarget(self, message_counter):
        return True

    def targetDetected(self):
        pass
