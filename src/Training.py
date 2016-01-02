import constants as c
import BCI

import copy


class Training(BCI.BCI):
    def __init__(self, connections, main_connection, recording, messages):
        BCI.BCI.__init__(self, connections, main_connection, recording, messages)
        self.packets = []
        self.expected_targets = []
        self.expected_target_index = -1
        self.target_freqs = {}

    def setupPackets(self):
        self.packets = self.recording.normal_eeg.list[0][c.EEG_RECORDING_PACKETS]
        self.target_freqs = self.recording.normal_eeg[0][c.EEG_RECORDING_FREQS]
        self.expected_targets = self.recording.expected_targets.list[0]
        self.expected_target_index = -1

    def setup(self, options):
        self.setupPackets()
        return BCI.BCI.setup(self, self.changeOptions(options))

    def start(self, options):
        return BCI.BCI.start(self, self.changeOptions(options))

    def changeOptions(self, options):
        options = copy.deepcopy(options)
        self.disableUnnecessaryOptions(options)
        self.setTrainingTime(options)
        options[c.DATA_FREQS] = self.target_freqs
        return options

    def disableUnnecessaryOptions(self, options):
        options[c.DATA_TRAINING][c.TRAINING_RECORD] = c.TRAINING_RECORD_DISABLED
        options[c.DATA_TEST][c.TEST_STANDBY] = c.TEST_NONE
        options[c.DATA_BACKGROUND][c.DISABLE] = 1
        options[c.DATA_ROBOT][c.DISABLE] = 1
        options[c.DATA_EMOTIV][c.DISABLE] = 1
        options[c.DATA_PLOTS] = {}

    def setTrainingTime(self, options):
        options[c.DATA_TEST][c.TEST_UNLIMITED] = False
        options[c.DATA_TEST][c.TEST_TIME] = self.getTotalTrainingTime()

    def getTotalTrainingTime(self):  # TODO test
        return len(self.packets)

    def getTarget(self, test_target, target_freqs, previous_target):  # TODO test
        if self.expected_target_index < len(self.expected_targets)-1:
            if self.expected_targets[self.expected_target_index+1][1] == self.message_counter:
                self.expected_target_index += 1
                return self.expected_targets[self.expected_target_index]

    def getNextPacket(self):
        return self.packets[self.message_counter]
