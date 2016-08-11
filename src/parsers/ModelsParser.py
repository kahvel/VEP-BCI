import constants as c


class ModelsOptionsParser(object):
    def parseLookBackTextbox(self, all_data):
        return int(all_data[c.MODELS_TAB_LOOK_BACK_LENGTH])

    def parseFeaturesToUse(self, all_data):
        data = all_data[c.MODELS_TAB_FEATURES_TO_USE]
        if data == "":
            return None
        else:
            return sorted(map(lambda x: x, data.strip('"').split('","')))

    def parseCvFolds(self, all_data):
        return int(all_data[c.MODELS_TAB_CV_FOLDS])

    def parseTargetCheckboxes(self, all_data, key):
        if all_data[key][key] is not None:
            return [int(number)-1 for number, enabled in all_data[key][key].items() if enabled == 1]
        else:
            return []

    def parseData(self, all_data):
        return {
            c.MODELS_PARSE_RECORDING_FOR_TRAINING: self.parseTargetCheckboxes(all_data, c.MODELS_TAB_RECORDING_FOR_TRAINING),
            c.MODELS_PARSE_RECORDING_FOR_VALIDATION: self.parseTargetCheckboxes(all_data, c.MODELS_TAB_RECORDING_FOR_VALIDATION),
            c.MODELS_PARSE_LOOK_BACK_LENGTH: self.parseLookBackTextbox(all_data),
            c.MODELS_PARSE_CV_FOLDS: self.parseCvFolds(all_data),
            c.MODELS_PARSE_FEATURES_TO_USE: self.parseFeaturesToUse(all_data),
        }


class ModelsParser(object):
    def __init__(self):
        self.options_parser = ModelsOptionsParser()

    def parseOptions(self, data):
        return self.options_parser.parseData(data)

    def parseAllData(self, all_data, model_number):
        return {
            c.MODELS_PARSE_OPTIONS: self.parseOptions(all_data[c.MODELS_NOTEBOOK][model_number][c.MODELS_TAB_OPTIONS_FRAME]),
            c.MODELS_TAB_MODEL_DATA: all_data[c.MODELS_NOTEBOOK][model_number][c.MODELS_TAB_MODEL_FRAME][c.MODELS_TAB_MODEL_DATA],
        }

    def parseData(self, all_data, model_number):
        if model_number is None:
            return None
        else:
            return self.parseAllData(all_data, model_number)