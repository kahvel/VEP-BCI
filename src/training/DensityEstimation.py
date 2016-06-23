from utils import readFeatures, featuresIterator
from TargetIdentification import ResultsParser
from ParameterHandler import NewTrainingParameterHandler

import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KernelDensity

import constants as c


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
            plt.subplot(5, 3, self.counter)
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
            self.setSubplot()
            parse_result[frequency] = {}
            for expected_frequency in self.frequencies_list:
                self.plotHistogram(result[frequency][expected_frequency])
                x = np.transpose([np.linspace(
                    min(result[frequency][expected_frequency]),
                    max(result[frequency][expected_frequency]),
                    len(result[frequency][expected_frequency])
                )])
                bandwidth = (x[1][0] - x[0][0])*3
                kde = KernelDensity(bandwidth=bandwidth)
                observations = np.transpose([result[frequency][expected_frequency]])
                kde.fit(observations)
                parse_result[frequency][expected_frequency] = kde
                self.plotKde(kde, x)
            # if self.plot_histogram or self.plot_kde:
            #     plt.title(str(tab) + str(method[0]) + str(harmonic) + str(frequency))


class NaiveBayes(ResultsParser):
    def __init__(self, frequencies_list):
        ResultsParser.__init__(self)
        self.frequencies_list = frequencies_list

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) != 0:
            result_dict = dict(result)
            for frequency in self.frequencies_list:
                for expected_frequency in self.frequencies_list:
                    log_value = data[frequency][expected_frequency].score_samples([[result_dict[frequency]]])[0]
                    value = np.exp(log_value)
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
        """
        Override to set self.parse_result = {} and to use self.data[tab][method] instead of self.data[tab].
        Should add method to options coming from main window, then overriding is not necessary.
        :param results:
        :return:
        """
        self.parse_result = {}
        for tab in results:
            for method in results[tab]:
                # if tab in self.data:
                    parse_result = self.parseResultValue(self.parse_result, tab)
                    parse_result = self.parseResultValue(parse_result, method)
                    if method[0] == c.CCA or method[0] == c.LRT:
                        if self.add_sum:
                            self.parseHarmonicResults(parse_result, {c.RESULT_SUM: results[tab][method]}, self.data[tab][method])
                        else:
                            self.parseHarmonicResults(parse_result, results[tab][method], self.data[tab][method])
                    elif method[0] == c.SUM_PSDA:
                        self.parseHarmonicResults(parse_result, results[tab][method], self.data[tab][method])
                    elif method[0] == c.PSDA:
                        self.parseSensorResults(parse_result, results[tab][method], self.data[tab][method])
        return self.parse_result


features_list, expected, frequencies = readFeatures(
    "../save/eeg_new_detrend2.txt",
    "C:\\Users\\Anti\\Desktop\\PycharmProjects\\MAProject\\src\\eeg\\eeg_new.txt",
    1
)


length = 256
step = 32

frequencies_list = sorted(frequencies.values())

result_parser = ResultCollector()
dummy_parameters = NewTrainingParameterHandler().numbersToOptions((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))["Weights"]
result_parser.setup(dummy_parameters)

for extracted_features, expected_target in featuresIterator(features_list, expected, length, step):
    expected_frequency = frequencies[expected_target]
    result_parser.setExpectedTarget(expected_frequency)
    result_parser.parseResults(extracted_features)

collected_results = result_parser.parse_result
print "density"
print collected_results
density_estimator = DensityEstimator(frequencies_list, plot_kde=True)
density_estimator.setup(dummy_parameters)
densities = density_estimator.parseResults(collected_results)
print densities

naive_bayes = NaiveBayes(frequencies_list)
naive_bayes.setup(densities)
for extracted_features, expected_target in featuresIterator(features_list, expected, length, step):
    print naive_bayes.parseResults(extracted_features)


plt.show()
