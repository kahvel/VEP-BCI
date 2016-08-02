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


class ResultsParser(object):
    def __init__(self, add_sum=True, data_has_method=False):
        self.data = None
        self.parse_result = None
        self.add_sum = add_sum
        self.data_has_method = data_has_method

    def setup(self, data):
        self.data = data

    def parseSensorResults(self, parse_result, results, data):
        for sensor in results:
            # if sensor in data:  # Currently data does not contain sensors
                self.parseHarmonicResults(self.parseResultValue(parse_result, sensor), results[sensor], data)

    def parseHarmonicResults(self, parse_result, results, data):
        for harmonic in results:
            if harmonic in data:
                self.parseFrequencyResults(self.parseResultValue(parse_result, harmonic), results[harmonic], data[harmonic])

    def parseFrequencyResults(self, parse_result, result, data):
        raise NotImplementedError("parseFrequencyResult not implemented!")

    def parseResultValue(self, parse_result, key):
        if key not in parse_result:
            parse_result[key] = {}
        return parse_result[key]

    def parseResults(self, results):
        for tab in results:
            for method in results[tab]:
                if tab in self.data:
                    parse_result = self.parseResultValue(self.parse_result, tab)
                    parse_result = self.parseResultValue(parse_result, method)
                    if self.data_has_method:
                        data = self.data[tab][method]
                    else:
                        data = self.data[tab]
                    if method[0] == c.CCA or method[0] == c.LRT:
                        if self.add_sum:
                            self.parseHarmonicResults(parse_result, {c.RESULT_SUM: results[tab][method]}, data)
                        else:
                            self.parseHarmonicResults(parse_result, results[tab][method], data)
                    elif method[0] == c.SUM_PSDA:
                        self.parseHarmonicResults(parse_result, results[tab][method], data)
                    elif method[0] == c.PSDA:
                        self.parseSensorResults(parse_result, results[tab][method], data)
                    elif method[0] == c.SNR_PSDA:
                        self.parseHarmonicResults(parse_result, results[tab][method], data)
        return self.parse_result


class WeightFinder(ResultsParser):
    def __init__(self):
        ResultsParser.__init__(self)

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) != 0:
            # total = result[0][1]/sum(map(lambda x: x[1], result))*data
            if result[0][0] in parse_result:
                parse_result[result[0][0]] += data
            else:
                parse_result[result[0][0]] = data

    def parseResultValue(self, parse_result, key):
        return parse_result

    def parseResults(self, results):
        self.parse_result = {}
        return ResultsParser.parseResults(self, results)


class DifferenceFinder(ResultsParser):
    def __init__(self):
        ResultsParser.__init__(self)
        self.comparison = []

    def parseResults(self, results):
        self.comparison = []
        self.parse_result = {}
        return ResultsParser.parseResults(self, results)

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) > 1:  # If we have at least 2 targets in the result dict
            difference = result[0][1]-result[1][1]
            parse_result[result[0][0], result[1][0]] = difference
            self.comparison.append(difference >= data)


class RatioFinder(ResultsParser):
    def __init__(self):
        ResultsParser.__init__(self)

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) != 0:
            for frequency, value in result:
                processed_value = self.getValue(value, result, data, frequency)
                parse_result[frequency] = processed_value

    def getValue(self, value, result, data, frequency):
        results_sum = sum(map(lambda x: data(x), dict(result).values()))
        return data(value)/results_sum

    def parseResults(self, results):
        self.parse_result = {}
        return ResultsParser.parseResults(self, results)


class TargetIdentification(object):
    def __init__(self, master_connection, results, new_results, standby):
        self.prev_results = ResultCounter()
        self.actual_results = ResultCounter()
        self.difference_finder = DifferenceFinder()
        self.weight_finder = WeightFinder()
        self.ratio_finder = RatioFinder()
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
            freq_weights = self.weight_finder.parseResults(results)
            differences = self.difference_finder.parseResults(results)
            difference_comparisons = self.difference_finder.comparison
            current_frequency = target_freqs[current_target] if current_target in target_freqs else None
            predicted_frequency = self.filterResults(freq_weights, target_freqs, current_frequency, difference_comparisons, filter_by_comparison)
            self.new_results.add(current_frequency, predicted_frequency)
            return predicted_frequency

    def handleFreqMessages(self, message, target_freqs, current_target, filter_by_comparison=True):
        results = message
        if results is not None:
            results = self.ratio_finder.parseResults(results)
            frequencies = sorted(target_freqs.values())
            psda_keys = [1, 2]
            cca_results_dict = dict(results[2][('CCA', ('P7', 'O1', 'O2', 'P8'))])["Sum"]
            for frequency in frequencies:
                self.matrix_result.append(cca_results_dict[frequency])
            for i, key in enumerate(psda_keys):
                psda_results = results[1][('Sum PSDA', ('P7', 'O1', 'O2', 'P8'))][key]
                psda_results_dict = dict(psda_results)
                for frequency in frequencies:
                    self.matrix_result.append(psda_results_dict[frequency])
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
