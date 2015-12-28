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

    def initialiseCounter(self, rounded_target_freqs):
        return {freq: 0 for freq in rounded_target_freqs}

    def reset(self, target_freqs):
        rounded_target_freqs = tuple(round(freq, 2) for freq in target_freqs)
        self.weights = []
        self.summed_weights = self.initialiseCounter(rounded_target_freqs)

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


class TargetIdentification(object):
    def __init__(self, master_connection, results, standby):
        self.prev_results = ResultCounter()
        self.actual_results = ResultCounter()
        self.need_new_target = None
        self.new_target_counter = None
        self.differences = []
        self.master_connection = master_connection
        self.results = results
        self.standby = standby
        self.method_weights = None
        self.method_differences = None

    def setup(self, weights, differences):
        self.method_weights = weights
        self.method_differences = differences

    def resetTargetVariables(self):
        self.need_new_target = False
        self.new_target_counter = 0

    def resetResults(self, freqs):
        rounded_target_freqs = tuple(round(freq, 2) for freq in freqs)
        self.prev_results.reset(rounded_target_freqs)
        self.actual_results.reset(rounded_target_freqs)

    def initialiseCounter(self, rounded_target_freqs):
        return {freq: 0 for freq in rounded_target_freqs}

    def countFrequencyResults(self, summed_weights, results, weight):
        summed_weights[round(results[0][0], 2)] += weight
        if len(results) > 1:  # If we have at least 2 targets in the result dict
            self.differences.append(results[0][1]-results[1][1])

    def countHarmonicResults(self, summed_weights, results, weight):
        for harmonic in results:
            if harmonic in weight:
                self.countFrequencyResults(summed_weights, results[harmonic], weight[harmonic])

    def countSensorResults(self, summed_weights, results, weight):
        for sensor in results:
            if sensor in weight:
                self.countHarmonicResults(summed_weights, results[sensor], weight)

    def countAll(self, results, target_freqs, weights):
        summed_weights = {round(freq, 2): 0 for freq in target_freqs}
        for tab in results:
            for method in results[tab]:
                if tab in weights:
                    if method[0] == c.CCA:
                        self.countFrequencyResults(summed_weights, results[tab][method], weights[tab][c.RESULT_SUM])
                    elif method[0] == c.SUM_PSDA:
                        self.countHarmonicResults(summed_weights, results[tab][method], weights[tab])
                    elif method[0] == c.PSDA:
                        self.countSensorResults(summed_weights, results[tab][method], weights[tab])
        return summed_weights

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
            print(self.differences, sum(self.differences))
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
            target_freqs_dict = target_freqs
            target_freqs = target_freqs_dict.values()
            rounded_target_freqs = tuple(round(freq, 2) for freq in target_freqs)
            self.differences = []
            freq_weights = self.countAll(results, target_freqs, self.method_weights)
            if all(map(lambda x: x > 0.1, self.differences)):
                frequency = self.prev_results.getFrequency(freq_weights)
                if frequency is not None:
                    result_frequency_rounded = self.actual_results.getFrequency({frequency: 1})
                    if result_frequency_rounded is not None:
                        result_frequency = target_freqs[rounded_target_freqs.index(result_frequency_rounded)]
                        self.handleStandby(result_frequency, target_freqs)
                        self.handleFinalResult(result_frequency, target_freqs_dict, current_target)
