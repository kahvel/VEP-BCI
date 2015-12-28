import constants as c


class TargetIdentification(object):
    def __init__(self, master_connection, results, standby):
        self.prev_results = []
        self.prev_results_counter = {}
        self.actual_results = []
        self.actual_results_counter = {}
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
        self.prev_results = []
        self.prev_results_counter = self.initialiseCounter(rounded_target_freqs)
        self.actual_results = []
        self.actual_results_counter = self.initialiseCounter(rounded_target_freqs)

    def initialiseCounter(self, rounded_target_freqs):
        return {freq: 0 for freq in rounded_target_freqs}

    def countFrequencyResults(self, counted_freqs, results, weight):
        counted_freqs[round(results[0][0], 2)] += weight
        self.differences.append(results[0][1]-results[1][1])

    def countHarmonicResults(self, counted_freqs, results, weight):
        for harmonic in results:
            if harmonic in weight:
                self.countFrequencyResults(counted_freqs, results[harmonic], weight[harmonic])

    def countSensorResults(self, counted_freqs, results, weight):
        for sensor in results:
            if sensor in weight:
                self.countHarmonicResults(counted_freqs, results[sensor], weight[sensor])

    def countAll(self, results, target_freqs, weight):
        counted_results = {round(freq, 2): 0 for freq in target_freqs}
        for tab in results:
            for method in results[tab]:
                if tab in weight and method[0] in weight[tab]:
                    if method[0] == c.CCA:
                        self.countFrequencyResults(counted_results, results[tab][method], weight[tab][method[0]])
                    elif method[0] == c.SUM_PSDA:
                        self.countHarmonicResults(counted_results, results[tab][method], weight[tab][method[0]])
                    elif method[0] == c.PSDA:
                        self.countSensorResults(counted_results, results[tab][method], weight[tab][method[0]])
        return counted_results

    def getDictKey(self, dict, value_arg):
        for key, value in dict.items():
            if value == value_arg:
                return key

    def handleFreqMessages(self, message, target_freqs, current_target):
        results = message
        if results is not None:
            target_freqs_dict = target_freqs
            target_freqs = target_freqs_dict.values()
            rounded_target_freqs = tuple(round(freq, 2) for freq in target_freqs)
            self.differences = []
            print results
            freq_weights = self.countAll(results, target_freqs, {6: {c.CCA: 1}, 5: {c.SUM_PSDA: {1.0: 0.5, c.RESULT_SUM: 0.5}}})
            if all(map(lambda x: x > 0.1, self.differences)):
                for freq in freq_weights:
                    self.prev_results_counter[freq] += freq_weights[freq]
                self.prev_results.append(freq_weights)
                if len(self.prev_results) > 1:
                    for result in self.prev_results[0]:
                        self.prev_results_counter[result] -= self.prev_results[0][result]
                    del self.prev_results[0]
                    f, m = max(self.prev_results_counter.items(), key=lambda x: x[1])
                    if m >= 1.5:
                        self.actual_results.append(f)
                        self.actual_results_counter[f] += 1
                        if len(self.actual_results) > 1:
                            self.actual_results_counter[self.actual_results[0]] -= 1
                            del self.actual_results[0]
                            f1, m1 = max(self.actual_results_counter.items(), key=lambda x: x[1])
                            max_freq = target_freqs[rounded_target_freqs.index(f1)]
                            if m1 >= 1:
                                if self.standby.enabled and self.standby.choseStandbyFreq(max_freq):
                                    # self.connections.sendPlotMessage(self.standby.in_standby_state and not self.standby.enabled)
                                    self.standby.switchStandby()
                                    self.master_connection.sendTargetMessage(self.standby.in_standby_state)
                                    # winsound.Beep(2500, 100)
                                    self.prev_results = []
                                if self.standby.notInStandby():
                                    self.master_connection.sendTargetMessage(max_freq)
                                    current = target_freqs_dict[current_target] if current_target in target_freqs_dict else None
                                    if not self.results.isPrevResult(max_freq):
                                        self.results.add(current, max_freq)
                                        self.master_connection.sendRobotMessage(self.getDictKey(target_freqs_dict, max_freq))
                                        print(self.differences, sum(self.differences))
                                        if max_freq != current:
                                            print("wrong", self.actual_results, self.actual_results_counter, self.prev_results_counter, current, f1)
                                        else:
                                            print("right", self.actual_results, self.actual_results_counter, self.prev_results_counter, current, f1)
                                    if max_freq == current:
                                        self.new_target_counter += 1
                                        if self.new_target_counter > 0:
                                            self.need_new_target = True
                                            self.new_target_counter = 0