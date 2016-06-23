from utils import readFeatures, featuresIterator
from TargetIdentification import ResultsParser
from ParameterHandler import NewTrainingParameterHandler

import matplotlib.pyplot as plt
import numpy as np

import constants as c


class ResultCollector(ResultsParser):
    def __init__(self):
        ResultsParser.__init__(self)
        self.expected_frequency = None
        self.parse_result = {}

    def setExpectedTarget(self, expected_frequency):
        self.expected_frequency = expected_frequency

    def parseResults(self, results):
        """
        Remove the first line "self.parse_result = {}", so the results remain in parse_result.
        Put it in constructor instead.
        :param results:
        :return:
        """
        for tab in results:
            for method in results[tab]:
                # if tab in self.data:
                    parse_result = self.parseResultValue(self.parse_result, tab)
                    if method[0] == c.CCA:
                        self.parseFrequencyResults(parse_result, results[tab][method], self.data[tab][c.RESULT_SUM])
                    elif method[0] == c.LRT:
                        self.parseFrequencyResults(parse_result, results[tab][method], self.data[tab][c.RESULT_SUM])
                    elif method[0] == c.SUM_PSDA:
                        self.parseHarmonicResults(parse_result, results[tab][method], self.data[tab])
                    elif method[0] == c.PSDA:
                        self.parseSensorResults(parse_result, results[tab][method], self.data[tab])
        return self.parse_result

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

    def parseResultValue(self, parse_result, key):
        if key not in parse_result:
            parse_result[key] = {}
        return parse_result[key]


features_list, expected, frequencies = readFeatures(
    "../save/eeg_new_detrend2.txt",
    "C:\\Users\\Anti\\Desktop\\PycharmProjects\\MAProject\\src\\eeg\\eeg_new.txt",
    1
)


length = 256
step = 32
packet_nr = 0
target = expected[0][0]
expected_index = 1

frequencies_list = sorted(frequencies.values())

first_sample = features_list[0]
density = {tab: {method: {harmonic: {frequency: {expected_frequency: [] for expected_frequency in frequencies_list} for frequency in frequencies_list} for harmonic in first_sample[tab][method]} for method in first_sample[tab]} for tab in first_sample}

result_parser = ResultCollector()
result_parser.setup(NewTrainingParameterHandler().numbersToOptions((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))["Weights"])

for extracted_features, expected_target in featuresIterator(features_list, expected, length, step):
    expected_frequency = frequencies[expected_target]
    result_parser.setExpectedTarget(expected_frequency)

# for extracted_features, expected_target in featuresIterator(features_list, expected, length, step):
#     for tab in extracted_features:
#         for method in extracted_features[tab]:
#             if c.SUM_PSDA in method:
#                 for harmonic in extracted_features[tab][method]:
#                     result_per_frequency = dict(extracted_features[tab][method][harmonic])
#                     for frequency in frequencies_list:
#                         expected_frequency = frequencies[expected_target]
#                         density[tab][method][harmonic][frequency][expected_frequency].append(result_per_frequency[frequency])
#
# counter = 1
# for tab in density:
#     for method in density[tab]:
#         for harmonic in density[tab][method]:
#             for frequency in frequencies_list:
#                 for expected_frequency in frequencies_list:
#                     bins = np.linspace(min(density[tab][method][harmonic][expected_frequency]), max(density[tab][method][harmonic][expected_frequency]), 10)
#                     plt.subplot(5, 3, counter)
#                     plt.hist(density[tab][method][harmonic][frequency][expected_frequency], bins=bins)
#                     counter += 1
#
# plt.show()
