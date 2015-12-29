import constants as c


class ResultCounter(object):
    def __init__(self):
        self.weights = []
        self.summed_weights = {}
        self.target_count_threshold = None
        self.weight_threshold = None

    def setup(self, target_threshold, weight_threshold):
        self.target_count_threshold = target_threshold
        self.weight_threshold = weight_threshold

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
        for result in self.weights[0]:
            self.summed_weights[result] -= self.weights[0][result]
        del self.weights[0]

    def frequencyWeightAboveThreshold(self):
        frequency, weight = max(self.summed_weights.items(), key=lambda x: x[1])
        if weight >= self.weight_threshold:
            return frequency

    def getFrequency(self, weights):
        self.addWeights(weights)
        if self.targetCountAboveThreshold():
            self.removeWeight()
            return self.frequencyWeightAboveThreshold()


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
        if result[0][0] in parse_result:
            parse_result[result[0][0]] += data
        else:
            parse_result[result[0][0]] = data

    def parseResultValue(self, parse_result, key):
        return parse_result


class DifferenceFinder(ResultsParser):
    def __init__(self):
        ResultsParser.__init__(self)

    def setup(self, data):
        self.data = data

    def parseResultValue(self, parse_result, key):
        if key not in parse_result:
            parse_result[key] = {}
        return parse_result[key]

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) > 1:  # If we have at least 2 targets in the result dict
            parse_result[result[0][0], result[1][0]] = result[0][1]-result[1][1]


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

    def setup(self, weights, differences):
        self.difference_finder.setup(differences)
        self.weight_finder.setup(weights)

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
        if not self.results.isPrevResult(result_frequency):
            self.results.add(current, result_frequency)
            self.master_connection.sendRobotMessage(self.getDictKey(target_freqs_dict, result_frequency))
            if result_frequency != current:
                print("wrong", self.actual_results.weights, self.actual_results.summed_weights, self.prev_results.summed_weights, current, result_frequency)
            else:
                print("right", self.actual_results.weights, self.actual_results.summed_weights, self.prev_results.summed_weights, current, result_frequency)

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
            self.holdResultTarget(result_frequency, current)

    def handleFreqMessages(self, message, target_freqs, current_target):
        results = message
        if results is not None:
            freq_weights = self.weight_finder.parseResults(results)
            differences = self.difference_finder.parseResults(results)
            if True or all(map(lambda x: x > 0.1, self.differences)):  # TODO fix this
                frequency = self.prev_results.getFrequency(freq_weights)
                if frequency is not None:
                    result_frequency = self.actual_results.getFrequency({frequency: 1})
                    if result_frequency is not None:
                        self.handleStandby(result_frequency, target_freqs.values())
                        self.handleFinalResult(result_frequency, target_freqs, current_target)
