import FeaturesParser
import constants as c
import pickle


class ResultCounter(object):
    def __init__(self):
        self.weights = []
        self.summed_weights = {}
        self.target_count_threshold = None
        self.weight_threshold = None
        self.always_remove_results = None

    def setup(self, options):
        self.target_count_threshold = options[c.DATA_TARGET_THRESHOLD]
        self.weight_threshold = options[c.DATA_WEIGHT_THRESHOLD]
        self.always_remove_results = options[c.DATA_ALWAYS_DELETE]

    def initialiseCounter(self, target_freqs):
        return {freq: 0 for freq in target_freqs}

    def reset(self, target_freqs):
        self.weights = []
        self.summed_weights = self.initialiseCounter(target_freqs)

    def addWeights(self, weights):
        for freq in weights:
            self.summed_weights[freq] += weights[freq]
        self.weights.append(weights)

    def targetCountAboveThreshold(self):
        return len(self.weights) >= self.target_count_threshold

    def removeWeight(self):
        if len(self.weights) > 0:
            for result in self.weights[0]:
                self.summed_weights[result] -= self.weights[0][result]
            del self.weights[0]

    def findMax(self):  # Let's find max if there is only one max.
        tie = False
        max_frequency, max_weight = None, -float("inf")
        for frequency, weight in self.summed_weights.items():
            if weight > max_weight:
                max_frequency, max_weight = frequency, weight
                tie = False
            elif weight == max_weight:
                tie = True
        if not tie:
            return max_frequency, max_weight
        else:
            return None, -float("inf")

    def maxFrequencyAboveThreshold(self):
        frequency, weight = self.findMax()
        if weight >= self.weight_threshold:
            return frequency

    def getFrequency(self, weights):
        self.addWeights(weights)
        if self.targetCountAboveThreshold():
            max_freq = self.maxFrequencyAboveThreshold()
            self.removeWeight()
            return max_freq


class TargetIdentification(object):
    def __init__(self, master_connection, results, new_results, standby):
        self.prev_results = ResultCounter()
        self.actual_results = ResultCounter()
        self.difference_finder = FeaturesParser.DifferenceFinder()
        self.weight_finder = FeaturesParser.WeightFinder()
        self.ratio_finder = FeaturesParser.RatioFinder()
        self.need_new_target = None
        self.new_target_counter = None
        self.master_connection = master_connection
        self.results = results
        self.new_results = new_results
        self.standby = standby
        self.clear_buffers = None
        self.saved_model = None
        self.matrix_result = None
        self.scaling_functions = None
        self.thresholds = None

    def setup(self, options):
        self.difference_finder.setup(options[c.DATA_EXTRACTION_DIFFERENCES])
        self.weight_finder.setup(options[c.DATA_EXTRACTION_WEIGHTS])
        self.prev_results.setup(options[c.DATA_PREV_RESULTS])
        self.actual_results.setup(options[c.DATA_ACTUAL_RESULTS])
        self.clear_buffers = options[c.DATA_CLEAR_BUFFERS]
        scaling_functions = self.getScalingFunction(pickle.load(file("U:\\data\\my\\pickle\\model11_mm.pkl")))
        self.scaling_functions = {
            1: {
                1: scaling_functions["PSDA_h1"],
                2: scaling_functions["PSDA_h2"],
            },
            2: {
                c.RESULT_SUM: scaling_functions["CCA"]
            }
        }
        self.saved_model = pickle.load(file("U:\\data\\my\\pickle\\model11.pkl"))
        self.thresholds = pickle.load(file("U:\\data\\my\\pickle\\model11_thresh.pkl"))
        self.ratio_finder.setup(self.scaling_functions)
        self.matrix_result = []

    def getScalingFunction(self, min_max):
        group_names = ["CCA", "PSDA_h1", "PSDA_h2"]#, "PSDA_sum"]
        functions = {}
        for group in group_names:
            minimum, maximum = min_max[group]
            functions[group] = lambda x: (x-minimum)/(maximum-minimum)
        return functions

    def resetTargetVariables(self):
        self.need_new_target = False
        self.new_target_counter = 0

    def resetResults(self, freqs):
        self.prev_results.reset(freqs)
        self.actual_results.reset(freqs)

    def initialiseCounter(self, rounded_target_freqs):
        return {freq: 0 for freq in rounded_target_freqs}

    def getDictKey(self, dict, value_arg):
        for key, value in dict.items():
            if value == value_arg:
                return key

    def handleStandby(self, result_frequency, target_freqs):
        if self.standby.enabled and self.standby.choseStandbyFreq(result_frequency):
            # self.connections.sendPlotMessage(self.standby.in_standby_state and not self.standby.enabled)
            self.standby.switchStandby()
            self.master_connection.sendTargetMessage(self.standby.in_standby_state)
            # winsound.Beep(2500, 100)
            self.prev_results.reset(target_freqs)

    def filterRepeatingResults(self, predicted_frequency, current_frequency, target_freqs_dict):
        if not self.clear_buffers:
            if not self.results.isPrevResult(predicted_frequency):
                self.sendCommand(predicted_frequency, current_frequency, target_freqs_dict)
        else:
            self.sendCommand(predicted_frequency, current_frequency, target_freqs_dict)
            self.clearBuffers(target_freqs_dict.values())

    def clearBuffers(self, target_freq):
        self.master_connection.sendClearBuffersMessage()
        self.actual_results.reset(target_freq)
        self.prev_results.reset(target_freq)

    def sendCommand(self, predicted_frequency, current_frequency, target_freqs_dict):
        self.master_connection.sendRobotMessage(self.getDictKey(target_freqs_dict, predicted_frequency))
        # self.printResult(predicted_frequency, current_frequency)
        self.results.add(current_frequency, predicted_frequency)
        self.holdResultTarget(predicted_frequency, current_frequency)

    def printResult(self, result_frequency, current):
        if result_frequency != current:
            print "wrong", current, result_frequency
        else:
            print "right", current, result_frequency

    def holdResultTarget(self, result_frequency, current):
        if result_frequency == current:
            self.new_target_counter += 1
            if self.new_target_counter > 0:
                self.need_new_target = True
                self.new_target_counter = 0

    def handleStandbyResult(self, result_frequency, target_freqs_dict, current_frequency):
        if self.standby.notInStandby():
            self.master_connection.sendTargetMessage(result_frequency)
            self.filterRepeatingResults(result_frequency, current_frequency, target_freqs_dict)

    def filterResults(self, freq_weights, target_freqs, current_frequency, difference_comparisons, filter_by_comparison):
        if sum(difference_comparisons) >= len(difference_comparisons) or not filter_by_comparison:
            frequency = self.prev_results.getFrequency(freq_weights)
            if frequency is not None:
                result_frequency = self.actual_results.getFrequency({frequency: 1})
                if result_frequency is not None:
                    self.handleStandby(result_frequency, target_freqs.values())
                    self.handleStandbyResult(result_frequency, target_freqs, current_frequency)
                return result_frequency
            elif self.actual_results.always_remove_results:
                self.actual_results.removeWeight()
        elif self.prev_results.always_remove_results:
            self.prev_results.removeWeight()
            self.actual_results.removeWeight()

    def handleFreqMessages1(self, message, target_freqs, current_target, filter_by_comparison=True):
        results = message
        if results is not None:
            freq_weights = self.weight_finder.parseResultsNewDict(results)
            differences = self.difference_finder.parseResultsNewDict(results)
            difference_comparisons = self.difference_finder.comparison
            current_frequency = target_freqs[current_target] if current_target in target_freqs else None
            predicted_frequency = self.filterResults(freq_weights, target_freqs, current_frequency, difference_comparisons, filter_by_comparison)
            self.new_results.add(current_frequency, predicted_frequency)
            return predicted_frequency

    def handleFreqMessages(self, message, target_freqs, current_target, filter_by_comparison=True):
        results = message
        if results is not None:
            results = self.ratio_finder.parseResultsNewDict(results)
            frequencies = sorted(target_freqs.values())
            psda_keys = [1, 2]
            # cca_results_dict = dict(results[2][('CCA', ('P7', 'O1', 'O2', 'P8'))])["Sum"]
            # for frequency in frequencies:
            #     self.matrix_result.append(cca_results_dict[frequency])
            # for i, key in enumerate(psda_keys):
            #     psda_results = results[1][('Sum PSDA', ('P7', 'O1', 'O2', 'P8'))][key]
            #     psda_results_dict = dict(psda_results)
            #     for frequency in frequencies:
            #         self.matrix_result.append(psda_results_dict[frequency])
            # cca_results_dict = dict(results[3][('LRT', ('P7', 'O1', 'O2', 'P8'))])["Sum"]
            # for frequency in frequencies:
            #     self.matrix_result.append(cca_results_dict[frequency])
            # for key in psda_keys:
            #     psda_results = results[4][('SNR PSDA', ('P7', 'O1', 'O2', 'P8'))][key]
            #     psda_results_dict = dict(psda_results)
            #     for frequency in frequencies:
            #         self.matrix_result.append(psda_results_dict[frequency])
            if len(self.matrix_result) == 90:
                # predicted = self.saved_model.predict([self.matrix_result])[0]
                scores = list(self.saved_model.decision_function([self.matrix_result])[0])
                predicted = None
                for i in range(len(scores)):
                    if scores[i] > self.thresholds[i] and all(map(lambda (j, (s, t)): s < t or j == i, enumerate(zip(scores, self.thresholds)))):
                        predicted = i
                        break
                if predicted is not None:
                    predicted_frequency = frequencies[predicted-1]
                    current_frequency = target_freqs[current_target] if current_target in target_freqs else None
                    self.new_results.add(current_frequency, predicted_frequency)
                    freq_weights = {predicted_frequency: 1.5}
                    predicted_frequency = self.filterResults(freq_weights, target_freqs, current_frequency, [True], False)
                    print predicted_frequency, current_frequency, self.saved_model.predict_proba([self.matrix_result]), self.saved_model.decision_function([self.matrix_result])
                    # self.matrix_result = self.matrix_result[9:]
                    self.matrix_result = []  # TODO to clear the array or not to clear?
                    return predicted_frequency
                else:
                    self.matrix_result = self.matrix_result[9:]
