import constants as c


class RecordParser(object):
    def __init__(self):
        pass

    def parseRecordingData(self, all_data, recording_number):
        if recording_number == c.EEG_SOURCE_DEVICE:
            return None
        else:
            return all_data[c.RECORD_NOTEBOOK][recording_number][c.EEG_FRAME][c.RECORDING_TAB_RECORDING_DATA]

    def parseData(self, all_data, recording_number):
        return {
            c.TRAINING_RECORD: all_data[c.TRAINING_RECORD][c.TRAINING_RECORD],
            c.RECORDING_TAB_RECORDING_DATA: self.parseRecordingData(all_data, recording_number)
        }
