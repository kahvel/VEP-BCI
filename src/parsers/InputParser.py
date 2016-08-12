import ClassificationParser
import ModelsParser
import constants as c


class AbstractInputParser(object):
    def __init__(self):
        self.classification_tab_parser = ClassificationParser.ClassificationParser()
        self.model_tab_parser = ModelsParser.ModelsParser()

    def parseFrequencies(self, enabled_targets):
        return {key: target[c.DATA_FREQ] for key, target in enabled_targets.items()}

    def parseHarmonicsTab(self, data, parse_function):
        return {key: parse_function(value[c.EXTRACTION_TAB_NOTEBOOK][c.EXTRACTION_TAB_HARMONICS_TAB]) for key, value in data.items()}

    def parseHarmonicData(self, data):
        return sorted(int(key) for key, value in data.items() if key.strip().isdigit() and value[key] == 1)

    def parseHarmonicTabTextboxes(self, data, textbox_name):
        return {key if key == c.RESULT_SUM else int(key): value[textbox_name] for key, value in data.items() if value[key] == 1}

    def parseWeightData(self, data):
        return self.parseHarmonicTabTextboxes(data, c.EXTRACTION_TAB_HARMONIC_WEIGHT)

    def parseDifferenceData(self, data):
        return self.parseHarmonicTabTextboxes(data, c.EXTRACTION_TAB_HARMONIC_DIFFERENCE)

    def parseTargetData(self, data):
        return {key: value.values()[0] for key, value in data.items()}

    def parsePlotNotebookData(self, data):
        return {key: value for key, value in data.items()}

    def parseExtractionTargets(self, data, target_freqs):
        return {int(key): target_freqs[int(key)] for key, value in data.items() if int(key) in target_freqs and data[key] == 1}

    def parseExtractionTab(self, data, target_freqs):
        return {
            c.DATA_EXTRACTION_OPTIONS: data[c.EXTRACTION_TAB_OPTIONS_TAB][c.OPTIONS_FRAME],
            c.DATA_EXTRACTION_SENSORS: data[c.EXTRACTION_TAB_ACTIVE_TAB][c.SENSORS_FRAME],
            c.DATA_EXTRACTION_METHODS: data[c.EXTRACTION_TAB_ACTIVE_TAB][c.METHODS_FRAME],
            c.DATA_EXTRACTION_TARGETS: self.parseExtractionTargets(data[c.EXTRACTION_TAB_ACTIVE_TAB][c.EXTRACTION_TAB_TARGETS_FRAME], target_freqs)
        }

    def parseExtractionOptions(self, data, target_data):
        return {key: self.parseExtractionTab(value[c.EXTRACTION_TAB_NOTEBOOK], target_data) for key, value in data.items()}

    def parseTestTab(self, data):
        if data[c.TEST_TAB_EEG_SOURCE_OPTION_MENU] == c.EEG_SOURCE_DEVICE:
            data[c.DISABLE] = False
        else:
            data[c.DISABLE] = True
            data[c.TEST_TAB_EEG_SOURCE_OPTION_MENU] = int(data[c.TEST_TAB_EEG_SOURCE_OPTION_MENU])
        return data

    def parseData(self, all_data):
        raise NotImplementedError("parseData not implemented!")


class TrainingInputParser(AbstractInputParser):
    def parseData(self, all_data):
        return {
            c.DATA_EXTRACTION: self.parseExtractionOptions(all_data[c.MAIN_NOTEBOOK_EXTRACTION_TAB], []),
            c.DATA_CLASSIFICATION: self.classification_tab_parser.parseData(all_data[c.MAIN_NOTEBOOK_CLASSIFICATION_TAB]),
            c.DATA_HARMONICS: self.parseHarmonicsTab(all_data[c.MAIN_NOTEBOOK_EXTRACTION_TAB], self.parseHarmonicData),
            c.DATA_RECORD: all_data[c.RECORD_NOTEBOOK_TAB],
            c.DATA_EXTRACTION_WEIGHTS: self.parseHarmonicsTab(all_data[c.MAIN_NOTEBOOK_EXTRACTION_TAB], self.parseWeightData),
            c.DATA_EXTRACTION_DIFFERENCES: self.parseHarmonicsTab(all_data[c.MAIN_NOTEBOOK_EXTRACTION_TAB], self.parseDifferenceData),
            c.DATA_CLEAR_BUFFERS: all_data[c.MAIN_NOTEBOOK_TEST_TAB][c.TEST_TAB_CLEAR_BUFFERS],
            c.DATA_PROCESS_SHORT_SIGNAL: all_data[c.MAIN_NOTEBOOK_TEST_TAB][c.TEST_TAB_PROCESS_SHORT_SIGNALS],
            c.DATA_TRAINING: all_data[c.MAIN_NOTEBOOK_TRAINING_TAB],
        }


class MainInputParser(AbstractInputParser):
    def parseData(self, all_data):
        target_data = self.parseTargetData(all_data[c.MAIN_NOTEBOOK_TARGETS_TAB][c.WINDOW_TAB_TARGETS_NOTEBOOK])
        target_freqs = self.parseFrequencies(target_data)
        model_number = self.classification_tab_parser.parseModelNumber(all_data[c.MAIN_NOTEBOOK_CLASSIFICATION_TAB])
        return {
            c.DATA_BACKGROUND: all_data[c.MAIN_NOTEBOOK_TARGETS_TAB][c.WINDOW_TAB_MONITOR_FRAME],
            c.DATA_TARGETS: target_data,
            c.DATA_FREQS: target_freqs,
            c.DATA_PLOTS: self.parsePlotNotebookData(all_data[c.MAIN_NOTEBOOK_PLOT_TAB]),
            c.DATA_EXTRACTION: self.parseExtractionOptions(all_data[c.MAIN_NOTEBOOK_EXTRACTION_TAB], target_freqs),
            c.DATA_CLASSIFICATION: self.classification_tab_parser.parseData(all_data[c.MAIN_NOTEBOOK_CLASSIFICATION_TAB]),
            c.DATA_MODEL: self.model_tab_parser.parseData(all_data[c.MAIN_NOTEBOOK_MODELS_TAB], model_number),
            c.DATA_HARMONICS: self.parseHarmonicsTab(all_data[c.MAIN_NOTEBOOK_EXTRACTION_TAB], self.parseHarmonicData),
            c.DATA_ROBOT: all_data[c.MAIN_NOTEBOOK_ROBOT_TAB],
            c.DATA_TEST: self.parseTestTab(all_data[c.MAIN_NOTEBOOK_TEST_TAB]),
            c.DATA_RECORD: all_data[c.MAIN_NOTEBOOK_RECORD_TAB][c.TRAINING_RECORD],
            c.DATA_EXTRACTION_WEIGHTS: self.parseHarmonicsTab(all_data[c.MAIN_NOTEBOOK_EXTRACTION_TAB], self.parseWeightData),
            c.DATA_EXTRACTION_DIFFERENCES: self.parseHarmonicsTab(all_data[c.MAIN_NOTEBOOK_EXTRACTION_TAB], self.parseDifferenceData),
            c.DATA_CLEAR_BUFFERS: all_data[c.MAIN_NOTEBOOK_TEST_TAB][c.TEST_TAB_CLEAR_BUFFERS],
            c.DATA_PROCESS_SHORT_SIGNAL: all_data[c.MAIN_NOTEBOOK_TEST_TAB][c.TEST_TAB_PROCESS_SHORT_SIGNALS],
        }
