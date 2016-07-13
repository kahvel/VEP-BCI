from utils import readFeaturesWithTargets, removeResultsAfterChange
from TargetIdentification import ResultsParser
from ParameterHandler import NewTrainingParameterHandler

import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KernelDensity
import pandas as pd


class Collector(ResultsParser):
    def __init__(self, add_sum, data_has_method):
        ResultsParser.__init__(self, add_sum=add_sum, data_has_method=data_has_method)
        self.expected_frequency = None

    def setExpectedTarget(self, expected_frequency):
        self.expected_frequency = expected_frequency

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) != 0:
            for frequency, value in result:
                processed_value = self.getValue(value, result, data, frequency)
                if frequency in parse_result:
                    if self.expected_frequency in parse_result[frequency]:
                        parse_result[frequency][self.expected_frequency].append(processed_value)
                    else:
                        parse_result[frequency][self.expected_frequency] = [processed_value]
                else:
                    parse_result[frequency] = {self.expected_frequency: [processed_value]}

    def getValue(self, value, result, data, frequency):
        raise NotImplementedError("getValue not implemented!")


class ResultCollector(Collector):
    def __init__(self):
        Collector.__init__(self, True, False)
        self.parse_result = {}

    def getValue(self, value, result, data, frequency):
        return value


class RatioCollector(Collector):
    def __init__(self):
        Collector.__init__(self, True, False)
        self.parse_result = {}

    def getValue(self, value, result, data, frequency):
        results_sum = sum(dict(result).values())
        return value/results_sum


class Normaliser(ResultsParser):
    def __init__(self, frequencies_list):
        ResultsParser.__init__(self, add_sum=False)
        self.frequencies_list = frequencies_list

    def parseFrequencyResults(self, parse_result, result, data):
        for frequency in self.frequencies_list:
            if frequency in result:
                parse_result[frequency] = {}
                mins = []
                maxs = []
                for expected_frequency in self.frequencies_list:
                    if expected_frequency in result[frequency]:
                        current_result = result[frequency][expected_frequency]
                        mins.append(min(current_result))
                        maxs.append(max(current_result))
                minimum = min(mins)
                maximum = max(maxs)
                self.addResult(parse_result, result, frequency, maximum, minimum)

    def addResult(self, parse_result, result, frequency, maximum, minimum):
        raise NotImplementedError("addResult not implemented!")

    def parseResults(self, results):
        self.parse_result = {}
        return ResultsParser.parseResults(self, results)


class NormaliserCreator(Normaliser):
    def addResult(self, parse_result, result, frequency, maximum, minimum):
        parse_result[frequency] = lambda x: (x-minimum)/(maximum-minimum)+1


class GroupNormaliser(Normaliser):
    def addResult(self, parse_result, result, frequency, maximum, minimum):
        for expected_frequency in self.frequencies_list:
            if expected_frequency in result[frequency]:
                current_result = result[frequency][expected_frequency]
                parse_result[frequency][expected_frequency] = map(lambda x: (x-minimum)/(maximum-minimum)+1, current_result)


class FeatureNormaliser(ResultsParser):
    def __init__(self, frequencies_list):
        ResultsParser.__init__(self, add_sum=True, data_has_method=True)
        self.frequencies_list = frequencies_list
        self.parse_result = {}

    def parseFrequencyResults(self, parse_result, result, data):
        result_dict = dict(result)
        for frequency in self.frequencies_list:
            if frequency in result_dict and frequency in data:
                current_result = result_dict[frequency]
                parse_result[frequency] = data[frequency](current_result)


class DensityEstimator(ResultsParser):
    def __init__(self, frequencies_list, figure, plot_kde=False, plot_histogram=False):
        ResultsParser.__init__(self, add_sum=False)
        self.counter = None
        self.plot_histogram = plot_histogram
        self.plot_kde = plot_kde
        self.frequencies_list = frequencies_list
        plt.figure(figure)

    def parseResults(self, results):
        self.counter = 1
        self.parse_result = {}
        return ResultsParser.parseResults(self, results)

    def setSubplot(self):
        if self.plot_histogram or self.plot_kde:
            plt.subplot(10, 5, self.counter)
        self.counter += 1

    def plotHistogram(self, data):
        if self.plot_histogram:
            bins = np.linspace(min(data), max(data), 50)
            plt.hist(data, bins=bins, normed=True, alpha=0.5)

    def plotKde(self, kde, x):
        if self.plot_kde:
            log_dens = kde.score_samples(x)
            plt.plot(x, np.exp(log_dens).T)

    def parseFrequencyResults(self, parse_result, result, data):
        for frequency in self.frequencies_list:
            if frequency in result:
                self.setSubplot()
                parse_result[frequency] = {}
                for expected_frequency in self.frequencies_list:
                    if expected_frequency in result[frequency]:
                        self.plotHistogram(result[frequency][expected_frequency])
                        x = np.transpose([np.linspace(
                            min(result[frequency][expected_frequency]),
                            max(result[frequency][expected_frequency]),
                            len(result[frequency][expected_frequency])
                        )])
                        bandwidth = (x[1][0] - x[0][0])*30
                        kde = KernelDensity(bandwidth=bandwidth)
                        observations = np.transpose([result[frequency][expected_frequency]])
                        kde.fit(observations)
                        parse_result[frequency][expected_frequency] = kde
                        self.plotKde(kde, x)
                # if self.plot_histogram or self.plot_kde:
                #     plt.title(str(tab) + str(method[0]) + str(harmonic) + str(frequency))


class NaiveBayes(ResultsParser):
    def __init__(self, frequencies_list):
        ResultsParser.__init__(self, add_sum=False, data_has_method=True)
        self.frequencies_list = frequencies_list

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) != 0:
            result_dict = dict(result)
            for frequency in self.frequencies_list:
                for expected_frequency in self.frequencies_list:
                    if frequency in result_dict and expected_frequency in data[frequency]:
                        log_value = data[frequency][expected_frequency].score_samples([[result_dict[frequency]]])[0]
                        value = np.exp(log_value)
                        if frequency in parse_result:
                            parse_result[frequency][expected_frequency] = value
                        else:
                            parse_result[frequency] = {expected_frequency: value}

    def parseResults(self, results):
        self.parse_result = {}
        return ResultsParser.parseResults(self, results)


class DensityGrouper(ResultsParser):
    def __init__(self, frequencies_list):
        ResultsParser.__init__(self, add_sum=False, data_has_method=False)
        self.frequencies_list = frequencies_list

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) != 0:
            for frequency in self.frequencies_list:
                if frequency in result:
                    for expected_frequency in self.frequencies_list:
                        if expected_frequency in result[frequency]:
                            value = result[frequency][expected_frequency]
                            if frequency in parse_result:
                                if expected_frequency in parse_result[frequency]:
                                    parse_result[frequency][expected_frequency].append(value)
                                else:
                                    parse_result[frequency][expected_frequency] = [value]
                            else:
                                parse_result[frequency] = {expected_frequency: [value]}

    def parseResultValue(self, parse_result, key):
        return parse_result

    def parseResults(self, results):
        self.parse_result = {}
        return ResultsParser.parseResults(self, results)


class MovingAverage(ResultsParser):
    def __init__(self, frequencies_list, window_length):
        ResultsParser.__init__(self, add_sum=False)
        self.frequencies_list = frequencies_list
        self.window_length = window_length

    def parseResults(self, results):
        self.parse_result = {}
        return ResultsParser.parseResults(self, results)

    def parseFrequencyResults(self, parse_result, result, data):
        for frequency in self.frequencies_list:
            if frequency in result:
                parse_result[frequency] = {}
                for expected_frequency in self.frequencies_list:
                    if expected_frequency in result[frequency]:
                        parse_result[frequency][expected_frequency] = movingAverage(result[frequency][expected_frequency], self.window_length)


def movingAverage(data, window_length):
    assert len(data) >= window_length
    ret = np.cumsum(data, dtype=float)
    ret[window_length:] = ret[window_length:] - ret[:-window_length]
    return list(ret[window_length - 1:] / window_length)


def multiplyDensities(frequencies_list, densities):
    result = {}
    for frequency in frequencies_list:
        if frequency in densities:
            result[frequency] = {}
            for expected_frequency in frequencies_list:
                if expected_frequency in densities[frequency]:
                    value = np.prod(densities[frequency][expected_frequency])
                    result[frequency][expected_frequency] = value
    return result


def multiplyDensitiesDifferentFrequencies(frequencies_list, densities):
    result = {}
    for expected_frequency in frequencies_list:
        value = 1
        for frequency in frequencies_list:
            if frequency in densities and expected_frequency in densities[frequency]:
                value *= densities[frequency][expected_frequency]
                # print frequency, expected_frequency, multiplied_results[frequency][expected_frequency]
        result[expected_frequency] = value
    return result


def collectData(collector):
    for i in [1,2,3,5,6,7,8,9,10,11,12,13,14,15]:
        training_x, training_y, training_frequencies = readFeaturesWithTargets(
            "U:\\data\\my\\results1_2_target\\results" + str(i) + ".txt",
            "U:\\data\\my\\results1_2_target\\frequencies" + str(i) + ".txt"
        )
        training_x, training_y = removeResultsAfterChange(training_x, training_y, number_of_steps_to_skip)
        for extracted_features, expected_target in zip(training_x, training_y):
            expected_frequency = training_frequencies[expected_target]
            collector.setExpectedTarget(expected_frequency)
            collector.parseResults(extracted_features)
    return collector, training_frequencies


length = 256
step = 32
number_of_steps_to_skip = 0
# number_of_steps_to_skip = length/step-1

dummy_parameters = NewTrainingParameterHandler().numbersToOptions((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))["Weights"]

feature_grouper = ResultCollector()
feature_grouper.setup(dummy_parameters)
feature_grouper, training_frequencies = collectData(feature_grouper)
grouped_features = feature_grouper.parse_result
# print grouped_features

# matrix = {}
# for tab, tab_results in grouped_features.items():
#     for method, method_results in tab_results.items():
#         for harmonic, harmonic_results in method_results.items():
#             for frequency, frequency_results in harmonic_results.items():
#                 for expected_frequency, expected_frequency_results in frequency_results.items():
#                     if expected_frequency in matrix:
#                         matrix[expected_frequency].append(expected_frequency_results)
#                     else:
#                         matrix[expected_frequency] = [expected_frequency_results]
# for i, expected_frequency in enumerate(matrix):
#     matrix[expected_frequency] = np.transpose(matrix[expected_frequency])
#     print matrix[expected_frequency].shape
#     # print matrix[expected_frequency]
#     plt.figure(i+1)
#     df = pd.DataFrame(matrix[expected_frequency])
#     axes = pd.tools.plotting.scatter_matrix(df, alpha=0.2)
#     # plt.tight_layout()
#
# plt.show()

# "C:\\Users\\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\src\\save\\test5_results_" + str(i) + ".txt",
# "C:\\Users\\Anti\\Desktop\\PycharmProjects\\MAProject\\src\\eeg\\test5.txt",

testing_x, testing_y, testing_frequencies = readFeaturesWithTargets(  # Check file names!
    "U:\\data\\my\\results1_2_target\\results15.txt",
    "U:\\data\\my\\results1_2_target\\frequencies15.txt"
)
testing_x, testing_y = removeResultsAfterChange(testing_x, testing_y, number_of_steps_to_skip)

frequencies_list = sorted(training_frequencies.values())
print frequencies_list

moving_average = MovingAverage(frequencies_list, 1)
moving_average.setup(dummy_parameters)
averaged_features = moving_average.parseResults(grouped_features)
# print averaged_features

group_normaliser = GroupNormaliser(frequencies_list)
group_normaliser.setup(dummy_parameters)
normalised_features = group_normaliser.parseResults(averaged_features)
# print normalised_features

density_estimator = DensityEstimator(frequencies_list, 1, plot_kde=True)
density_estimator.setup(dummy_parameters)
density_functions = density_estimator.parseResults(normalised_features)
# print density_functions

normaliser_creator = NormaliserCreator(frequencies_list)
normaliser_creator.setup(dummy_parameters)
normaliser_functions = normaliser_creator.parseResults(averaged_features)
# print normaliser_functions

# ratio_collector = RatioCollector()
# ratio_collector.setup(dummy_parameters)
# ratio_collector, _ = collectData(ratio_collector)
# ratios = ratio_collector.parse_result
# # print ratios
#
# ratio_group_normaliser = GroupNormaliser(frequencies_list)
# ratio_group_normaliser.setup(dummy_parameters)
# normalised_ratios = ratio_group_normaliser.parseResults(ratios)
# # print normalised_ratios
#
# ratio_density_estimator = DensityEstimator(frequencies_list, 2, plot_kde=True)
# ratio_density_estimator.setup(dummy_parameters)
# ratio_density_functions = ratio_density_estimator.parseResults(normalised_ratios)

# plt.show()

feature_normaliser = FeatureNormaliser(frequencies_list)
feature_normaliser.setup(normaliser_functions)

density_grouper = DensityGrouper(frequencies_list)
density_grouper.setup(dummy_parameters)

naive_bayes = NaiveBayes(frequencies_list)
naive_bayes.setup(density_functions)

correct = 0
wrong = 0


class MovingAverageCollector(ResultsParser):
    def __init__(self, window_length):
        ResultsParser.__init__(self)
        self.window_length = window_length
        self.is_short = True
        self.expected_frequency = None
        self.parse_result = {}

    def newExpectedTarget(self, expected_frequency):
        if expected_frequency != self.expected_frequency:
            self.is_short = True
            self.parse_result = {}
            self.expected_frequency = expected_frequency

    def parseFrequencyResults(self, parse_result, result, data):
        for frequency, value in result:
            result_dict = dict(result)
            if frequency in parse_result:
                parse_result[frequency] = self.addValue(parse_result[frequency], result_dict[frequency])
            else:
                parse_result[frequency] = [result_dict[frequency]]

    def addValue(self, parse_result, value):
        if len(parse_result) >= self.window_length:
            self.is_short = False
            return parse_result[1:] + [value]
        else:
            return parse_result + [value]

    def parseResults(self, results):
        res = ResultsParser.parseResults(self, results)
        if not self.is_short:
            return res
        else:
            return None


class MovingAverageOnTestSet(ResultsParser):
    def __init__(self, window_length):
        ResultsParser.__init__(self, add_sum=False)
        self.window_length = window_length

    def parseFrequencyResults(self, parse_result, result, data):
        for frequency, value in result.items():
            parse_result[frequency] = movingAverage(result[frequency], self.window_length)[0]

    def parseResults(self, results):
        self.parse_result = {}
        return ResultsParser.parseResults(self, results)


window_length = 1
prev_results = MovingAverageCollector(window_length)
prev_results.setup(dummy_parameters)

test_moving_average = MovingAverageOnTestSet(window_length)
test_moving_average.setup(dummy_parameters)

for extracted_features, expected_target in zip(testing_x, testing_y):
    prev_results.newExpectedTarget(expected_target)
    collected = prev_results.parseResults(extracted_features)
    if collected is not None:  # None if length < window_length
        averaged = test_moving_average.parseResults(collected)
        normalised_features = feature_normaliser.parseResults(averaged)
        densities = naive_bayes.parseResults(normalised_features)  # TODO density is sometimes 0
        # print densities
        grouped_densities = density_grouper.parseResults(densities)
        # print grouped_densities
        multiplied_densities = multiplyDensities(frequencies_list, grouped_densities)
        # print multiplied_densities
        multiplied_densities_final = multiplyDensitiesDifferentFrequencies(frequencies_list, multiplied_densities)
        # print multiplied_densities_final
        expected_frequency = testing_frequencies[expected_target]
        predicted_frequency = sorted(map(lambda x: (x[1], x[0]), multiplied_densities_final.items()), reverse=True)[0][1]
        correct += expected_frequency == predicted_frequency
        wrong += expected_frequency != predicted_frequency
        if expected_frequency == predicted_frequency:
            print "Correct",
        else:
            print "Wrong  ",
        print round(expected_frequency, 2), round(predicted_frequency, 2), correct, wrong

print correct, wrong


plt.show()
