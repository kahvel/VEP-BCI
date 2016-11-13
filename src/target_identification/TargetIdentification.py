from parsers import FeaturesParser
from target_identification.models import LdaModel, SvmModel, QdaModel, TransitionModel
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
    def __init__(self):
        self.prev_results = ResultCounter()
        self.actual_results = ResultCounter()
        self.difference_finder = FeaturesParser.DifferenceFinder()
        self.weight_finder = FeaturesParser.WeightFinder()
        self.ratio_finder = FeaturesParser.RatioFinder()
        self.results = None
        self.model = None
        self.second_model = None
        self.thresholds = None
        self.classification_type_options = None
        self.setup_succeeded = True
        self.prev_result_weight_threshold = None

    def setup(self, options):
        self.setup_succeeded = True
        self.classification_type_options = options[c.DATA_CLASSIFICATION][c.CLASSIFICATION_PARSE_TYPE]
        model_number = options[c.DATA_CLASSIFICATION][c.CLASSIFICATION_PARSE_MODEL]
        if self.classification_type_options == c.CLASSIFICATION_TYPE_NEW and model_number == c.CLASSIFICATION_MODEL_NONE:
            self.setup_succeeded = False
            print "Error: New classification method but no model chosen!"
        self.difference_finder.setup(options[c.DATA_EXTRACTION_DIFFERENCES])
        self.weight_finder.setup(options[c.DATA_EXTRACTION_WEIGHTS])
        self.prev_results.setup(options[c.DATA_CLASSIFICATION][c.CLASSIFICATION_PARSE_PREV_RESULTS])
        self.actual_results.setup(options[c.DATA_CLASSIFICATION][c.CLASSIFICATION_PARSE_ACTUAL_RESULTS])
        self.prev_result_weight_threshold = 1  # self.getPrevResultWeightThreshold(options)
        # self.ratio_finder.setup(self.scaling_functions)
        if self.classification_type_options == c.CLASSIFICATION_TYPE_NEW and model_number != c.CLASSIFICATION_MODEL_NONE:
            self.setupModel(options[c.DATA_MODEL][c.MODELS_TAB_MODEL_DATA], options[c.DATA_MODEL][c.MODELS_PARSE_OPTIONS])

    def getPrevResultWeightThreshold(self, options):
        option = options[c.DATA_CLASSIFICATION][c.CLASSIFICATION_PARSE_PREV_RESULTS][c.DATA_WEIGHT_THRESHOLD]
        return option if option > 0 else 1

    def setupSucceeded(self):
        return self.setup_succeeded

    def setupModel(self, model_data, model_options):
        minimum, maximum = model_data[c.MODELS_TAB_MIN_MAX]
        model = model_data[c.MODELS_TAB_MODEL]
        second_model = model_data[c.MODELS_TAB_SECOND_MODEL]
        self.thresholds = model_data[c.MODELS_TAB_THRESHOLDS]
        features_to_use = model_options[c.MODELS_PARSE_FEATURES_TO_USE]
        sample_count = model_options[c.MODELS_PARSE_LOOK_BACK_LENGTH]
        self.model = LdaModel.OnlineLdaModel()
        # self.model = SvmModel.OnlineSvmModel()
        # self.model = QdaModel.OnlineQdaModel()
        self.model.setup(minimum, maximum, features_to_use, sample_count, model)
        self.second_model = TransitionModel.OnlineModel()
        self.second_model.setup(features_to_use, 10, second_model)

    def resetPrevResults(self, freqs):
        self.prev_results.reset(freqs)
        self.actual_results.reset(freqs)

    def setResults(self, results):
        self.results = results

    def filterResults(self, freq_weights, difference_comparisons, filter_by_comparison):
        if sum(difference_comparisons) >= len(difference_comparisons) or not filter_by_comparison:
            frequency = self.prev_results.getFrequency(freq_weights)
            if frequency is not None:
                return self.actual_results.getFrequency({frequency: 1})
            elif self.actual_results.always_remove_results:
                self.actual_results.removeWeight()
        elif self.prev_results.always_remove_results:
            self.prev_results.removeWeight()
            self.actual_results.removeWeight()

    def handleFreqMessagesOld(self, message, target_freqs, filter_by_comparison=True):
        results = message
        if results is not None:
            freq_weights = self.weight_finder.parseResultsNewDict(results)
            differences = self.difference_finder.parseResultsNewDict(results)
            difference_comparisons = self.difference_finder.comparison
            predicted_frequency = self.filterResults(freq_weights, difference_comparisons, filter_by_comparison)
            return predicted_frequency

    def handleFreqMessagesNew(self, features, target_freqs, filter_by_comparison=True):
        if features is not None:
            ratios = self.model.buildRatioMatrix(features)
            combined_ratios = self.model.collectSamples(ratios[0])
            if combined_ratios is not None:
                scores1 = list(self.model.decisionFunction([combined_ratios])[0])
                print scores1
                combined = self.second_model.collectSamples(scores1)
                if combined is not None:
                    print combined
                    scores = list(self.second_model.predictProba([combined])[0])

                    # print self.second_model.predict(self.model.decisionFunction([combined_ratios]))
                #     weights = list(score - threshold for score, threshold in zip(scores, self.thresholds))
                #     weigths_dict = {freq: weights[key-1] for key, freq in target_freqs.items()}
                #     predicted_frequency = self.filterResults(weigths_dict, [True], False)
                #     if predicted_frequency is not None:
                #         self.model.resetCollectedSamples()  # TODO to clear the array or not to clear?
                #     return predicted_frequency
                # # else:
                # #     self.filterResults({}, [False], True)

                    predicted = None
                    for i in range(len(scores)):
                        if scores[i] > self.thresholds[i]*1.2 and all(map(lambda (j, (s, t)): s < t*0.8 or j == i, enumerate(zip(scores, self.thresholds)))):
                            predicted = i
                            break
                    # predicted = self.model.predict([combined_ratios])[0]
                    if predicted is not None:
                        predicted_target = self.model.getOrderedLabels()[predicted]
                        predicted_frequency = target_freqs[predicted_target]
                        freq_weights = {predicted_frequency: self.prev_result_weight_threshold}
                        predicted_frequency = self.filterResults(freq_weights, [True], False)
                        # print predicted_frequency, current_frequency, self.model.decisionFunction(combined_ratios)
                        if predicted_frequency is not None:
                            self.model.resetCollectedSamples()  # TODO to clear the array or not to clear?
                            self.second_model.resetCollectedSamples()
                        return predicted_frequency
                    # else:  # This else branch instead of always_delete options
                    #     freq_weights = {freq: 0 for freq in target_freqs.values()}
                    #     self.filterResults(freq_weights, [True], False)
                    #     return None

    def handleFreqMessages(self, features, old_features, target_freqs, filter_by_comparison=True):
        if self.classification_type_options == c.CLASSIFICATION_TYPE_NEW:
            return self.handleFreqMessagesNew(features, target_freqs, filter_by_comparison)
        elif self.classification_type_options == c.CLASSIFICATION_TYPE_OLD:
            return self.handleFreqMessagesOld(old_features, target_freqs, filter_by_comparison)
        elif self.classification_type_options == c.CLASSIFICATION_TYPE_NONE:
            return
