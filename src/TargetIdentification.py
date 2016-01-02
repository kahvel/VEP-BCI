import constants as c


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
    def __init__(self):
        self.data = None
        self.parse_result = None

    def setup(self, *args):
        raise NotImplementedError("setup not implemented!")

    def parseSensorResults(self, parse_result, results, data):
        for sensor in results:
            # if sensor in data:  # Currently data does not contain sensors
                self.parseHarmonicResults(self.parseResultValue(parse_result, sensor), results[sensor], data)

    def parseHarmonicResults(self, parse_result, results, data):
        for harmonic in results:
            # if harmonic in self.data:
                self.parseFrequencyResults(self.parseResultValue(parse_result, harmonic), results[harmonic], data[harmonic])

    def parseFrequencyResults(self, parse_result, result, data):
        raise NotImplementedError("parseFrequencyResult not implemented!")

    def parseResultValue(self, parse_result, key):
        raise NotImplementedError("parseResultValue not implemented!")

    def parseResults(self, results):
        self.parse_result = {}
        for tab in results:
            for method in results[tab]:
                # if tab in self.data:
                    parse_result = self.parseResultValue(self.parse_result, tab)
                    if method[0] == c.CCA:
                        self.parseFrequencyResults(parse_result, results[tab][method], self.data[tab][c.RESULT_SUM])
                    elif method[0] == c.SUM_PSDA:
                        self.parseHarmonicResults(parse_result, results[tab][method], self.data[tab])
                    elif method[0] == c.PSDA:
                        self.parseSensorResults(parse_result, results[tab][method], self.data[tab])
        return self.parse_result


class WeightFinder(ResultsParser):
    def __init__(self):
        ResultsParser.__init__(self)

    def setup(self, data):
        self.data = data

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) != 0:
            if result[0][0] in parse_result:
                parse_result[result[0][0]] += data
            else:
                parse_result[result[0][0]] = data

    def parseResultValue(self, parse_result, key):
        return parse_result


class DifferenceFinder(ResultsParser):
    def __init__(self):
        ResultsParser.__init__(self)
        self.comparison = []

    def setup(self, data):
        self.data = data

    def parseResults(self, results):
        self.comparison = []
        return ResultsParser.parseResults(self, results)

    def parseResultValue(self, parse_result, key):
        if key not in parse_result:
            parse_result[key] = {}
        return parse_result[key]

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) > 1:  # If we have at least 2 targets in the result dict
            difference = result[0][1]-result[1][1]
            parse_result[result[0][0], result[1][0]] = difference
            self.comparison.append(difference > data)


class TargetIdentification(object):
    def __init__(self, master_connection, results, standby):
        self.prev_results = ResultCounter()
        self.actual_results = ResultCounter()
        self.difference_finder = DifferenceFinder()
        self.weight_finder = WeightFinder()
        self.need_new_target = None
        self.new_target_counter = None
        self.master_connection = master_connection
        self.results = results
        self.standby = standby
        self.clear_buffers = None

    def setup(self, options):
        self.difference_finder.setup(options[c.DATA_EXTRACTION_DIFFERENCES])
        self.weight_finder.setup(options[c.DATA_EXTRACTION_WEIGHTS])
        self.prev_results.setup(options[c.DATA_PREV_RESULTS])
        self.actual_results.setup(options[c.DATA_ACTUAL_RESULTS])
        self.clear_buffers = options[c.DATA_CLEAR_BUFFERS]

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

    def filterRepeatingResults(self, result_frequency, current, target_freqs_dict):
        if not self.clear_buffers:
            if not self.results.isPrevResult(result_frequency):
                self.addResultAndSendCommand(result_frequency, current, target_freqs_dict)
        else:
            self.addResultAndSendCommand(result_frequency, current, target_freqs_dict)
            self.clearBuffers(target_freqs_dict.values())

    def clearBuffers(self, target_freq):
        self.master_connection.sendClearBuffersMessage()
        self.actual_results.reset(target_freq)
        self.prev_results.reset(target_freq)

    def addResultAndSendCommand(self, result_frequency, current, target_freqs_dict):
        self.results.add(current, result_frequency)
        self.master_connection.sendRobotMessage(self.getDictKey(target_freqs_dict, result_frequency))
        self.printResult(result_frequency, current)
        self.holdResultTarget(result_frequency, current)

    def printResult(self, result_frequency, current):
        if result_frequency != current:
            print "wrong",
        else:
            print "right",
        print self.actual_results.weights, self.actual_results.summed_weights, self.prev_results.summed_weights, current, result_frequency

    def holdResultTarget(self, result_frequency, current):
        if result_frequency == current:
            self.new_target_counter += 1
            if self.new_target_counter > 0:
                self.need_new_target = True
                self.new_target_counter = 0

    def handleFinalResult(self, result_frequency, target_freqs_dict, current_target):
        if self.standby.notInStandby():
            self.master_connection.sendTargetMessage(result_frequency)
            current = target_freqs_dict[current_target] if current_target in target_freqs_dict else None
            self.filterRepeatingResults(result_frequency, current, target_freqs_dict)

    def handleFreqMessages(self, message, target_freqs, current_target):
        results = message
        if results is not None:
            freq_weights = self.weight_finder.parseResults(results)
            differences = self.difference_finder.parseResults(results)
            if all(self.difference_finder.comparison):
                frequency = self.prev_results.getFrequency(freq_weights)
                if frequency is not None:
                    result_frequency = self.actual_results.getFrequency({frequency: 1})
                    if result_frequency is not None:
                        self.handleStandby(result_frequency, target_freqs.values())
                        self.handleFinalResult(result_frequency, target_freqs, current_target)
                elif self.actual_results.always_remove_results:
                    self.actual_results.removeWeight()
            elif self.prev_results.always_remove_results:
                self.prev_results.removeWeight()
                self.actual_results.removeWeight()
