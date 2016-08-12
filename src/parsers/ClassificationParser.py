import constants as c


class ClassificationParser(object):
    def parseIdentificationResultParameters(self, all_data, frame_name):
        return {
            c.DATA_TARGET_THRESHOLD: all_data[c.CLASSIFICATION_TAB_FILTER_OPTIONS_FRAME][frame_name][c.CLASSIFICATION_TAB_RESULT_COUNTER],
            c.DATA_WEIGHT_THRESHOLD: all_data[c.CLASSIFICATION_TAB_FILTER_OPTIONS_FRAME][frame_name][c.CLASSIFICATION_TAB_RESULT_THRESHOLD],
            c.DATA_ALWAYS_DELETE:    all_data[c.CLASSIFICATION_TAB_FILTER_OPTIONS_FRAME][frame_name][c.CLASSIFICATION_TAB_ALWAYS_DELETE],
        }

    def parseModelNumber(self, all_data):
        value = all_data[c.CLASSIFICATION_TAB_CONTROL_FRAME][c.CLASSIFICATION_TAB_MODEL_OPTION_MENU]
        if value == c.CLASSIFICATION_MODEL_NONE:
            return c.CLASSIFICATION_MODEL_NONE
        else:
            return int(value)

    def parseData(self, all_data):
        return {
            c.CLASSIFICATION_PARSE_ACTUAL_RESULTS: self.parseIdentificationResultParameters(all_data, c.CLASSIFICATION_TAB_RESULT_FILTER_FRAME),
            c.CLASSIFICATION_PARSE_PREV_RESULTS: self.parseIdentificationResultParameters(all_data, c.CLASSIFICATION_TAB_PREV_RESULT_FILTER_FRAME),
            c.CLASSIFICATION_PARSE_TYPE: all_data[c.CLASSIFICATION_TAB_CONTROL_FRAME][c.CLASSIFICATION_TAB_TYPE_OPTION_MENU],
            c.CLASSIFICATION_PARSE_MODEL: all_data[c.CLASSIFICATION_TAB_CONTROL_FRAME][c.CLASSIFICATION_TAB_MODEL_OPTION_MENU],
        }
