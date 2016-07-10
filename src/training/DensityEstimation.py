from utils import readFeatures, featuresIterator
from TargetIdentification import ResultsParser
from ParameterHandler import NewTrainingParameterHandler

import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KernelDensity


class ResultCollector(ResultsParser):
    def __init__(self):
        ResultsParser.__init__(self)
        self.expected_frequency = None
        self.parse_result = {}

    def setExpectedTarget(self, expected_frequency):
        self.expected_frequency = expected_frequency

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) != 0:
            for frequency, value in result:
                if frequency in parse_result:
                    if self.expected_frequency in parse_result[frequency]:
                        parse_result[frequency][self.expected_frequency].append(value)
                    else:
                        parse_result[frequency][self.expected_frequency] = [value]
                else:
                    parse_result[frequency] = {self.expected_frequency: [value]}


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
            if frequency in result_dict:
                current_result = result_dict[frequency]
                parse_result[frequency] = data[frequency](current_result)


class DensityEstimator(ResultsParser):
    def __init__(self, frequencies_list, plot_kde=False, plot_histogram=False):
        ResultsParser.__init__(self, add_sum=False)
        self.counter = None
        self.plot_histogram = plot_histogram
        self.plot_kde = plot_kde
        self.frequencies_list = frequencies_list

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

train_length = 256
train_step = 32

test_length = 256
test_step = 32

dummy_parameters = NewTrainingParameterHandler().numbersToOptions((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))["Weights"]

feature_grouper = ResultCollector()
feature_grouper.setup(dummy_parameters)
for i in [1,2,3,5,6,7,8,9,10,11,12,13,14,15]:
    result_file_name = "U:\\data\\my\\results1_2\\results" + str(i) + ".txt"
    eeg_file_name = "U:\\data\\my\\eeg1\\" + str(i) + ".txt"
    training_x, training_y, training_frequencies = readFeatures(
        result_file_name,
        eeg_file_name,
        1
    )
    for extracted_features, expected_target in featuresIterator(training_x, training_y, train_length, train_step, skip_after_change=False):
        expected_frequency = training_frequencies[expected_target]
        feature_grouper.setExpectedTarget(expected_frequency)
        feature_grouper.parseResults(extracted_features)
grouped_features = feature_grouper.parse_result
# print grouped_features

# "C:\\Users\\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\src\\save\\test5_results_" + str(i) + ".txt",
# "C:\\Users\\Anti\\Desktop\\PycharmProjects\\MAProject\\src\\eeg\\test5.txt",

testing_x, testing_y, testing_frequencies = readFeatures(  # Check file names!
    "U:\\data\\my\\results1_2\\results15.txt",
    "U:\\data\\my\\eeg1\\15.txt",
    1
)

frequencies_list = sorted(training_frequencies.values())
print frequencies_list

group_normaliser = GroupNormaliser(frequencies_list)
group_normaliser.setup(dummy_parameters)
normalised_features = group_normaliser.parseResults(grouped_features)
# print normalised_features

density_estimator = DensityEstimator(frequencies_list, plot_kde=True)
density_estimator.setup(dummy_parameters)
density_functions = density_estimator.parseResults(normalised_features)
# print density_functions

normaliser_creator = NormaliserCreator(frequencies_list)
normaliser_creator.setup(dummy_parameters)
normaliser_functions = normaliser_creator.parseResults(grouped_features)
# print normaliser_functions

feature_normaliser = FeatureNormaliser(frequencies_list)
feature_normaliser.setup(normaliser_functions)

density_grouper = DensityGrouper(frequencies_list)
density_grouper.setup(dummy_parameters)

naive_bayes = NaiveBayes(frequencies_list)
naive_bayes.setup(density_functions)

correct = 0
wrong = 0

for extracted_features, expected_target in featuresIterator(testing_x, testing_y, test_length, test_step, skip_after_change=False):
    normalised_features = feature_normaliser.parseResults(extracted_features)
    densities = naive_bayes.parseResults(normalised_features)
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
    # if expected_frequency == predicted_frequency:
    #     print "Correct",
    # else:
    #     print "Wrong  ",
    # print round(expected_frequency, 2), round(predicted_frequency, 2), correct, wrong

print correct, wrong


plt.show()
