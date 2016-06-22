import Results
import TargetIdentification
import Standby
import constants as c

from ParameterHandler import NewTrainingParameterHandler
from utils import readFeatures, featuresIterator

import scipy.optimize
import numpy as np


class DummyMasterConnection(object):
    def __init__(self):
        self.results = []

    def sendClearBuffersMessage(self):
        pass

    def sendTargetMessage(self, message):
        if not isinstance(message, bool):
            self.results.append(message)

    def sendRobotMessage(self, command):
        pass


results = Results.Results()
results.isPrevResult = lambda x: False
standby = Standby.Standby()
standby.disable()
master_connection = DummyMasterConnection()
target_identification = TargetIdentification.TargetIdentification(master_connection, results, standby)

# trial_number = 1
# features_list, expected, frequencies = readFeatures(
#     "../save/test5_results_" + str(trial_number) + ".txt",
#     "C:\\Users\\Anti\\Desktop\\PycharmProjects\\MAProject\\src\\eeg\\test5.txt",
#     trial_number
# )

features_list, expected, frequencies = readFeatures(
    "../save/eeg_new_detrend2.txt",
    "C:\\Users\\Anti\\Desktop\\PycharmProjects\\MAProject\\src\\eeg\\eeg_new.txt",
    1
)

parameter_handler = NewTrainingParameterHandler()

counter = 0
length = 256
step = 32
packet_count = len(features_list)*step+length


def costFunction(numbers, options_handler, frequencies):
    global counter
    new_options = options_handler.numbersToOptions(numbers)
    # all_options[c.DATA_EXTRACTION_WEIGHTS] = new_options[c.DATA_EXTRACTION_WEIGHTS]
    # all_options[c.DATA_EXTRACTION_DIFFERENCES] = new_options[c.DATA_EXTRACTION_DIFFERENCES]
    # new_options[c.DATA_ACTUAL_RESULTS][c.DATA_ALWAYS_DELETE]= all_options[c.DATA_ACTUAL_RESULTS][c.DATA_ALWAYS_DELETE]
    # new_options[c.DATA_PREV_RESULTS][c.DATA_ALWAYS_DELETE] = all_options[c.DATA_PREV_RESULTS][c.DATA_ALWAYS_DELETE]
    # all_options[c.DATA_ACTUAL_RESULTS] = new_options[c.DATA_ACTUAL_RESULTS]
    # all_options[c.DATA_PREV_RESULTS] = new_options[c.DATA_PREV_RESULTS]
    # print new_options
    target_identification.results.start(frequencies.values())
    target_identification.resetTargetVariables()
    target_identification.setup(new_options)
    target_identification.resetResults(frequencies.values())
    for result, expected_target in featuresIterator(features_list, expected, length, step):
        target_identification.handleFreqMessages(result, frequencies, expected_target)
    target_identification.results.trialEnded(packet_count)
    print target_identification.results
    wrong_result_count = target_identification.results.list[-1]["Wrong"]
    correct_result_count = target_identification.results.list[-1]["Correct"]
    result = target_identification.results.list[-1]["Wrong"] - target_identification.results.list[-1]["Correct"]
    result = len(features_list) if wrong_result_count == 0 and correct_result_count == 0 else result
    # if counter % 100 == 0 or True:
    #     print "Result", correct_result_count, wrong_result_count
    counter += 1
    print "Result", correct_result_count, wrong_result_count, result
    return result
    # total = target_identification.results.list[-1]["Wrong"] + target_identification.results.list[-1]["Correct"]
    # return -total+result
    # return -correct_result_count


# result = scipy.optimize.differential_evolution(
#     costFunction,
#     parameter_handler.getBounds(),
#     args=(parameter_handler, frequencies),
#     popsize=20,
#     seed=99,
#     disp=True
# )
# print counter
# print result
costFunction(
    (1, 1, None, 1, 1, 0.01, 0.01, None, 0.02, 0.005, 1, 0.005),
    parameter_handler,
    frequencies
)
