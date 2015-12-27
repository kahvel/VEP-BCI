import constants as c


class InputParser(object):
    def parseFrequencies(self, enabled_targets):
        return {key: target[c.DATA_FREQ] for key, target in enabled_targets.items()}

    def parseHarmonicsTab(self, data, parse_function):
        return {key: parse_function(value[c.EXTRACTION_TAB_NOTEBOOK][c.EXTRACTION_TAB_HARMONICS_TAB]) for key, value in data.items()}

    def parseHarmonicData(self, data):
        return sorted(int(key) for key, value in data.items() if key.strip().isdigit() and value[key] == 1)

    def parseHarmonicTabTextboxes(self, data, textbox_name):
        return {key if key == c.RESULT_SUM else int(key): value[textbox_name] for key, value in data.items() if value[key] == 1}

    def parseWeightData(self, data):
        return self.parseHarmonicTabTextboxes(data, c.HARMONIC_WEIGHT)

    def parseDifferenceData(self, data):
        return self.parseHarmonicTabTextboxes(data, c.HARMONIC_DIFFERENCE)

    def parseTargetData(self, data):
        return {key: value.values()[0] for key, value in data.items()}

    def parsePlotNotebookData(self, data):
        return {key: value for key, value in data.items()}

    def parseExtractionNotebookData(self, data):
        return {key: value[c.EXTRACTION_TAB_NOTEBOOK][c.EXTRACTION_TAB_OPTIONS_TAB] for key, value in data.items()}

    def parseData(self, all_data):
        target_data = self.parseTargetData(all_data[c.TARGETS_NOTEBOOK])
        return {
            c.DATA_BACKGROUND: all_data[c.WINDOW_TAB],
            c.DATA_TARGETS: target_data,
            c.DATA_FREQS: self.parseFrequencies(target_data),
            c.DATA_PLOTS: self.parsePlotNotebookData(all_data[c.PLOT_NOTEBOOK]),
            c.DATA_EXTRACTION: self.parseExtractionNotebookData(all_data[c.EXTRACTION_NOTEBOOK]),
            c.DATA_TEST: all_data[c.TEST_TAB],
            c.DATA_HARMONICS: self.parseHarmonicsTab(all_data[c.EXTRACTION_NOTEBOOK], self.parseHarmonicData),
            c.DATA_ROBOT: all_data[c.ROBOT_TAB],
            c.DATA_EMOTIV: all_data[c.EMOTIV_TAB],
            c.DATA_TRAINING: all_data[c.TRAINING_TAB],
            c.DATA_WEIGHTS: self.parseHarmonicsTab(all_data[c.EXTRACTION_NOTEBOOK], self.parseWeightData),
            c.DATA_DIFFERENCES: self.parseHarmonicsTab(all_data[c.EXTRACTION_NOTEBOOK], self.parseDifferenceData)
        }
