import constants as c


class InputParser(object):
    def getFrequencies(self, enabled_targets):
        return {key: target[c.DATA_FREQ] for key, target in enabled_targets.items()}

    def getHarmonics(self, data):
        return {key: self.parseHarmonicData(value[c.EXTRACTION_TAB_NOTEBOOK][c.EXTRACTION_TAB_HARMONICS_TAB]) for key, value in data.items()}

    def parseHarmonicData(self, data):
        return [int(key) for key, value in data.items() if key.strip().isdigit() and value[key] == 1]

    def getTargetData(self, data):
        return {key: value.values()[0] for key, value in data.items()}

    def getPlotNotebookData(self, data):
        return {key: value for key, value in data.items()}

    def getExtractionNotebookData(self, data):
        return {key: value[c.EXTRACTION_TAB_NOTEBOOK][c.EXTRACTION_TAB_OPTIONS_TAB] for key, value in data.items()}

    def getData(self, all_data):
        target_data = self.getTargetData(all_data[c.TARGETS_NOTEBOOK])
        return {
            c.DATA_BACKGROUND: all_data[c.WINDOW_TAB],
            c.DATA_TARGETS: target_data,
            c.DATA_FREQS: self.getFrequencies(target_data),
            c.DATA_PLOTS: self.getPlotNotebookData(all_data[c.PLOT_NOTEBOOK]),
            c.DATA_EXTRACTION: self.getExtractionNotebookData(all_data[c.EXTRACTION_NOTEBOOK]),
            c.DATA_TEST: all_data[c.TEST_TAB],
            c.DATA_HARMONICS: self.getHarmonics(all_data[c.EXTRACTION_NOTEBOOK]),
            c.DATA_ROBOT: all_data[c.ROBOT_TAB],
            c.DATA_EMOTIV: all_data[c.EMOTIV_TAB],
            c.DATA_TRAINING: all_data[c.TRAINING_TAB]
        }
