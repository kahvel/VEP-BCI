import constants as c


class ClassificationParser(object):
    def parseLookBackTextbox(self, all_data):
        return int(all_data[c.CLASSIFICATION_TAB_OPTIONS_FRAME][c.CLASSIFICATION_TAB_LOOK_BACK_LENGTH])

    def parseFeaturesToUse(self, all_data):
        data = all_data[c.CLASSIFICATION_TAB_OPTIONS_FRAME][c.CLASSIFICATION_TAB_FEATURES_TO_USE]
        if data == "":
            return None
        else:
            return sorted(map(lambda x: x.strip('"'), data.split(",")))

    def parseCvFolds(self, all_data):
        return int(all_data[c.CLASSIFICATION_TAB_OPTIONS_FRAME][c.CLASSIFICATION_TAB_CV_FOLDS])

    def parseTargetCheckboxes(self, all_data, key):
        return [int(number)-1 for number, enabled in all_data[key][key].items() if enabled == 1]

    def parseIdentificationResultParameters(self, all_data, frame_name):
        return {
            c.DATA_TARGET_THRESHOLD: all_data[c.CLASSIFICATION_TAB_FILTER_OPTIONS_FRAME][frame_name][c.CLASSIFICATION_TAB_RESULT_COUNTER],
            c.DATA_WEIGHT_THRESHOLD: all_data[c.CLASSIFICATION_TAB_FILTER_OPTIONS_FRAME][frame_name][c.CLASSIFICATION_TAB_RESULT_THRESHOLD],
            c.DATA_ALWAYS_DELETE:    all_data[c.CLASSIFICATION_TAB_FILTER_OPTIONS_FRAME][frame_name][c.CLASSIFICATION_TAB_ALWAYS_DELETE],
        }

    def parseData(self, all_data):
        return {
            c.CLASSIFICATION_PARSE_LOOK_BACK_LENGTH: self.parseLookBackTextbox(all_data),
            c.CLASSIFICATION_PARSE_CV_FOLDS: self.parseCvFolds(all_data),
            c.CLASSIFICATION_PARSE_FEATURES_TO_USE: self.parseFeaturesToUse(all_data),
            c.CLASSIFICATION_PARSE_RECORDING_FOR_TRAINING: self.parseTargetCheckboxes(all_data, c.CLASSIFICATION_TAB_RECORDING_FOR_TRAINING),
            c.CLASSIFICATION_PARSE_RECORDING_FOR_VALIDATION: self.parseTargetCheckboxes(all_data, c.CLASSIFICATION_TAB_RECORDING_FOR_VALIDATION),
            c.CLASSIFICATION_PARSE_ACTUAL_RESULTS: self.parseIdentificationResultParameters(all_data, c.CLASSIFICATION_TAB_RESULT_FILTER_FRAME),
            c.CLASSIFICATION_PARSE_PREV_RESULTS: self.parseIdentificationResultParameters(all_data, c.CLASSIFICATION_TAB_PREV_RESULT_FILTER_FRAME),
        }
