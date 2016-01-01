import constants as c
import BCI

import copy


class Training(BCI.BCI):
    def __init__(self, connections, main_connection, recording):
        BCI.BCI.__init__(self, connections, main_connection, recording)
        self.packets = []
        self.packet_index = -1
        self.expected_targets = []
        self.expected_target_index = -1

    def setupPackets(self):
        self.packets = self.recording.normal_eeg.list[0]
        self.expected_targets = self.recording.expected_targets.list[0]
        self.expected_target_index = -1
        self.packet_index = -1

    def setup(self, options):
        BCI.BCI.setup(self, self.changeOptions(options))

    def start(self, options):
        BCI.BCI.start(self, self.changeOptions(options))

    def changeOptions(self, options):
        options = copy.deepcopy(options)
        self.disableUnnecessaryOptions(options)
        self.setTrainingTime(options)
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
        self.packet_index += 1
        return self.packets[self.packet_index]
