import constants as c


class TestParser(object):
    def __init__(self):
        pass

    def parseRecordingNumber(self, all_data):
        value = all_data[c.TEST_TAB_EEG_SOURCE_OPTION_MENU]
        if value == c.EEG_SOURCE_DEVICE:
            return c.EEG_SOURCE_DEVICE
        else:
            return int(value)

    def addDisable(self, all_data):
        all_data[c.DISABLE] = all_data[c.TEST_TAB_EEG_SOURCE_OPTION_MENU] != c.EEG_SOURCE_DEVICE

    def addEegSource(self, data):
        if data[c.TEST_TAB_EEG_SOURCE_OPTION_MENU] != c.EEG_SOURCE_DEVICE:
            data[c.TEST_TAB_EEG_SOURCE_OPTION_MENU] = int(data[c.TEST_TAB_EEG_SOURCE_OPTION_MENU])

    def parseData(self, all_data):
        self.addDisable(all_data)
        self.addEegSource(all_data)
        return all_data
