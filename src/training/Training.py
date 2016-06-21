import Results
import TargetIdentification
import Standby
import constants as c

from ParameterHandler import NewTrainingParameterHandler

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

trial_number = 1
# file_content = open("../save/test5_results_" + str(trial_number) + ".txt").readlines()
file_content = open("../save/eeg_new_detrend2.txt").readlines()
# frequencies = dict(enumerate(sorted(map(lambda x: x[0], eval(file_content[0])[1][('Sum PSDA', ('P7', 'O1', 'O2', 'P8'))][1]))))
features_list = []
for result in file_content:
    features_list.append(eval(result))

# file_content = open("C:\\Users\\Anti\\Desktop\\PycharmProjects\\MAProject\\src\\eeg\\test5.txt").read().split(";")
file_content = open("C:\\Users\\Anti\\Desktop\\PycharmProjects\\MAProject\\src\\eeg\\eeg_new.txt").read().split(";")
frequencies = eval(file_content[0])[trial_number-1][c.EEG_RECORDING_FREQS]
expected = eval(file_content[2])[trial_number-1]

parameter_handler = NewTrainingParameterHandler()

print frequencies
print expected
print len(features_list)
# print len(eval(file_content[0])[trial_number-1]["Packets"])

counter = 0
length = 256
step = 32
packet_nr = 3
target = expected[0][0]
expected_index = 1


def costFunction(numbers, options_handler, frequencies):
    global counter, expected_index, target
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
    for i, result in enumerate(features_list):
        if i == 0:
            packet_nr = length
        else:
            packet_nr = length + step * i

        if expected_index < len(expected) and packet_nr >= expected[expected_index][1]:
            target = expected[expected_index][0]
            expected_index += 1

        target_identification.handleFreqMessages(result, frequencies, target)
        # print i, packet_nr, target
    target_identification.results.trialEnded(packet_nr)
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

