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

    def parseIdentificationResultParameters(self, data, frame_name):
        return {
            c.DATA_TARGET_THRESHOLD: data[c.TEST_TAB][c.IDENTIFICATION_OPTIONS_FRAME][frame_name][c.TEST_RESULT_COUNTER],
            c.DATA_WEIGHT_THRESHOLD: data[c.TEST_TAB][c.IDENTIFICATION_OPTIONS_FRAME][frame_name][c.TEST_RESULT_THRESHOLD],
            c.DATA_ALWAYS_DELETE:    data[c.TEST_TAB][c.IDENTIFICATION_OPTIONS_FRAME][frame_name][c.TEST_ALWAYS_DELETE],
        }

    def parseData(self, all_data):
        target_data = self.parseTargetData(all_data[c.TARGETS_NOTEBOOK])
        target_freqs = self.parseFrequencies(target_data)
        return {
            c.DATA_BACKGROUND: all_data[c.WINDOW_TAB],
            c.DATA_TARGETS: target_data,
            c.DATA_FREQS: target_freqs,
            c.DATA_PLOTS: self.parsePlotNotebookData(all_data[c.PLOT_NOTEBOOK]),
            c.DATA_EXTRACTION: self.parseExtractionOptions(all_data[c.EXTRACTION_NOTEBOOK], target_freqs),
            c.DATA_TEST: all_data[c.TEST_TAB],
            c.DATA_HARMONICS: self.parseHarmonicsTab(all_data[c.EXTRACTION_NOTEBOOK], self.parseHarmonicData),
            c.DATA_ROBOT: all_data[c.ROBOT_TAB],
            c.DATA_EMOTIV: all_data[c.EMOTIV_TAB],
            c.DATA_RECORD: all_data[c.RECORD_TAB],
            c.DATA_EXTRACTION_WEIGHTS: self.parseHarmonicsTab(all_data[c.EXTRACTION_NOTEBOOK], self.parseWeightData),
            c.DATA_EXTRACTION_DIFFERENCES: self.parseHarmonicsTab(all_data[c.EXTRACTION_NOTEBOOK], self.parseDifferenceData),
            c.DATA_ACTUAL_RESULTS: self.parseIdentificationResultParameters(all_data, c.TEST_RESULT_COUNTER_FRAME),
            c.DATA_PREV_RESULTS: self.parseIdentificationResultParameters(all_data, c.TEST_PREV_RESULT_COUNTER_FRAME),
            c.DATA_CLEAR_BUFFERS: all_data[c.TEST_TAB][c.IDENTIFICATION_OPTIONS_FRAME][c.TEST_CLEAR_BUFFERS],
            c.DATA_PROCESS_SHORT_SIGNAL: all_data[c.TEST_TAB][c.IDENTIFICATION_OPTIONS_FRAME][c.TEST_PROCESS_SHORT_SIGNALS],
        }
