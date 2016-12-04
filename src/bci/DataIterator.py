import constants as c


class AbstractDataIterator(object):
    def __init__(self, bci):
        self.index = None
        self.length = None
        self.bci = bci

    def setupIndexAndLength(self, length):
        self.index = 0
        self.length = length

    def getIndexAndIncrease(self):
        if self.index >= self.length - 1:
            self.bci.setExitFlag(True)
        self.index += 1
        return self.index - 1


class DataIterator(AbstractDataIterator):
    def __init__(self, connections, bci):
        AbstractDataIterator.__init__(self, bci)
        self.connections = connections
        self.source_option = None
        self.eeg_or_features_option = None
        self.eeg = None
        self.features = None
        self.index = None

    def setup(self, options):
        self.source_option = options[c.DATA_TEST][c.TEST_TAB_EEG_SOURCE_OPTION_MENU]
        self.eeg_or_features_option = options[c.DATA_TEST][c.TEST_TAB_RECORDED_TYPE_OPTION_MENU]
        if self.source_option != c.EEG_SOURCE_DEVICE:
            self.eeg = options[c.DATA_RECORD][c.RECORDING_TAB_RECORDING_DATA][c.RECORDING_TAB_EEG].getData()
            self.features = options[c.DATA_RECORD][c.RECORDING_TAB_RECORDING_DATA][c.RECORDING_TAB_FEATURES].getData()
            self.setupIndexAndLength(self.getLength())

    def getLength(self):
        if self.eeg_or_features_option == c.TEST_RECORDED_TYPE_EEG:
            return len(self.eeg)
        elif self.eeg_or_features_option == c.TEST_RECORDED_TYPE_FEATURES:
            return len(self.features)

    def getNextPacket(self):
        if self.source_option == c.EEG_SOURCE_DEVICE:
            return self.connections.receiveEmotivMessage()
        else:
            if self.eeg_or_features_option == c.TEST_RECORDED_TYPE_EEG:
                return self.eeg[self.getIndexAndIncrease()]
            elif self.eeg_or_features_option == c.TEST_RECORDED_TYPE_FEATURES:
                return "dummyNotNoneReturnValue"

    def getFeatures(self):
        if self.source_option == c.EEG_SOURCE_DEVICE:
            return self.connections.receiveExtractionMessage()
        else:
            if self.eeg_or_features_option == c.TEST_RECORDED_TYPE_EEG:
                return self.connections.receiveExtractionMessage()
            elif self.eeg_or_features_option == c.TEST_RECORDED_TYPE_FEATURES:
                return self.features[self.getIndexAndIncrease()]
