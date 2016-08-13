from parsers import FeaturesParser
from target_identification import LdaModel
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


class TargetIdentification(object):
    def __init__(self, master_connection, standby):
        self.prev_results = ResultCounter()
        self.actual_results = ResultCounter()
        self.difference_finder = FeaturesParser.DifferenceFinder()
        self.weight_finder = FeaturesParser.WeightFinder()
        self.ratio_finder = FeaturesParser.RatioFinder()
        self.need_new_target = None
        self.new_target_counter = None
        self.master_connection = master_connection
        self.results = None
        self.new_results = None
        self.standby = standby
        self.clear_buffers = None
        self.allow_repeating = None
        self.model = None
        self.thresholds = None
        self.classification_type_options = None
        self.setup_succeeded = True

    def setup(self, options):
        self.setup_succeeded = True
        self.classification_type_options = options[c.DATA_CLASSIFICATION][c.CLASSIFICATION_PARSE_TYPE]
        model_number = options[c.DATA_CLASSIFICATION][c.CLASSIFICATION_PARSE_MODEL]
        if self.classification_type_options == c.CLASSIFICATION_TYPE_NEW and model_number == c.CLASSIFICATION_MODEL_NONE:
            self.setup_succeeded = False
            print "Error: New classification method but no model chosen!"
        self.allow_repeating = options[c.DATA_TEST][c.TEST_TAB_ALLOW_REPEATING]
        self.difference_finder.setup(options[c.DATA_EXTRACTION_DIFFERENCES])
        self.weight_finder.setup(options[c.DATA_EXTRACTION_WEIGHTS])
        self.prev_results.setup(options[c.DATA_CLASSIFICATION][c.CLASSIFICATION_PARSE_PREV_RESULTS])
        self.actual_results.setup(options[c.DATA_CLASSIFICATION][c.CLASSIFICATION_PARSE_ACTUAL_RESULTS])
        self.clear_buffers = options[c.DATA_CLEAR_BUFFERS]
        # self.ratio_finder.setup(self.scaling_functions)
        if self.classification_type_options == c.CLASSIFICATION_TYPE_NEW and model_number != c.CLASSIFICATION_MODEL_NONE:
            self.setupModel(options[c.DATA_MODEL][c.MODELS_TAB_MODEL_DATA], options[c.DATA_MODEL][c.MODELS_PARSE_OPTIONS])

    def setupSucceeded(self):
        return self.setup_succeeded

    def setupModel(self, model_data, model_options):
        minimum, maximum = model_data[c.MODELS_TAB_MIN_MAX]
        model = model_data[c.MODELS_TAB_MODEL]
        self.thresholds = model_data[c.MODELS_TAB_THRESHOLDS]
        features_to_use = model_options[c.MODELS_PARSE_FEATURES_TO_USE]
        sample_count = model_options[c.MODELS_PARSE_LOOK_BACK_LENGTH]
        self.model = LdaModel.OnlineLdaModel()
        self.model.setup(minimum, maximum, features_to_use, sample_count, model)

    def resetNeedNewTarget(self):
        self.need_new_target = False
        self.new_target_counter = 0

    def resetPrevResults(self, freqs):
        self.prev_results.reset(freqs)
        self.actual_results.reset(freqs)

    def setResults(self, results, new_results):
        self.results = results
        self.new_results = new_results

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
        if self.allow_repeating or not self.allow_repeating and not self.results.isEqualToPreviousResult(predicted_frequency):
            self.chooseTarget(predicted_frequency, current_frequency, target_freqs_dict)

    def clearBuffers(self, target_freq):
        if self.clear_buffers:
            self.master_connection.sendClearBuffersMessage()
            self.actual_results.reset(target_freq)
            self.prev_results.reset(target_freq)

    def chooseTarget(self, predicted_frequency, current_frequency, target_freqs_dict):
        self.master_connection.sendRobotMessage(self.getDictKey(target_freqs_dict, predicted_frequency))
        # self.printResult(predicted_frequency, current_frequency)
        self.results.add(current_frequency, predicted_frequency)
        self.holdResultTarget(predicted_frequency, current_frequency)
        self.clearBuffers(target_freqs_dict.values())

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

    def handleFreqMessagesOld(self, message, target_freqs, current_target, filter_by_comparison=True):
        results = message
        if results is not None:
            freq_weights = self.weight_finder.parseResultsNewDict(results)
            differences = self.difference_finder.parseResultsNewDict(results)
            difference_comparisons = self.difference_finder.comparison
            current_frequency = target_freqs[current_target] if current_target in target_freqs else None
            predicted_frequency = self.filterResults(freq_weights, target_freqs, current_frequency, difference_comparisons, filter_by_comparison)
            self.new_results.add(current_frequency, predicted_frequency)
            return predicted_frequency

    def handleFreqMessagesNew(self, features, target_freqs, current_target, filter_by_comparison=True):
        if features is not None:
            ratios = self.model.buildRatioMatrix(features)
            print ratios
            combined_ratios = self.model.collectSamples(ratios[0])
            if combined_ratios is not None:
                print combined_ratios
                scores = list(self.model.decisionFunction([combined_ratios])[0])
                print scores
                predicted = None
                for i in range(len(scores)):
                    if scores[i] > self.thresholds[i] and all(map(lambda (j, (s, t)): s < t or j == i, enumerate(zip(scores, self.thresholds)))):
                        predicted = i
                        break
                if predicted is not None:
                    predicted_target = self.model.getOrderedLabels()[predicted]
                    predicted_frequency = target_freqs[predicted_target]
                    current_frequency = target_freqs[current_target] if current_target in target_freqs else None
                    self.new_results.add(current_frequency, predicted_frequency)
                    freq_weights = {predicted_frequency: float("inf")}
                    predicted_frequency = self.filterResults(freq_weights, target_freqs, current_frequency, [True], False)
                    # print predicted_frequency, current_frequency, self.model.decisionFunction(combined_ratios)
                    self.model.resetCollectedSamples()  # TODO to clear the array or not to clear?
                    return predicted_frequency

    def handleFreqMessages(self, features, old_features, target_freqs, current_target, filter_by_comparison=True):
        if self.classification_type_options == c.CLASSIFICATION_TYPE_NEW:
            self.handleFreqMessagesNew(features, target_freqs, current_target, filter_by_comparison)
        elif self.classification_type_options == c.CLASSIFICATION_TYPE_OLD:
            self.handleFreqMessagesOld(old_features, target_freqs, current_target, filter_by_comparison)
        elif self.classification_type_options == c.CLASSIFICATION_TYPE_NONE:
            pass
