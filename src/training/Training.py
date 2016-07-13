import Results
import TargetIdentification
import Standby
import constants as c

from ParameterHandler import NewTrainingParameterHandler, BruteForceHandler
from utils import readFeaturesWithTargets, removeResultsAfterChange

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
standby = Standby.Standby()
standby.disable()
master_connection = DummyMasterConnection()
target_identification = TargetIdentification.TargetIdentification(master_connection, results, standby)

features_list, expected, frequencies = readFeaturesWithTargets(
    "U:\\data\\my\\results1_2_target\\results5.txt",
    "U:\\data\\my\\results1_2_target\\frequencies5.txt"
)

# frequencies[4] = (frequencies.values()[0] + frequencies.values()[1])/2
# frequencies[5] = (frequencies.values()[2] + frequencies.values()[1])/2
print frequencies

length = 256
step = 32
number_of_steps_to_skip = length/step-1

features_list, expected = removeResultsAfterChange(features_list, expected, 0)
packet_count = len(features_list)*step+length

enable_buffer_clearing = False


def costFunction(numbers, options_handler, frequencies):
    new_options = options_handler.numbersToOptions(numbers)
    target_identification.results.start(frequencies.values())
    target_identification.resetTargetVariables()
    target_identification.setup(new_options)
    target_identification.resetResults(frequencies.values())
    clear_buffers = False
    packet_counter = 0
    for result, expected_target in zip(features_list, expected):
        if clear_buffers and enable_buffer_clearing:
            packet_counter += step
            if packet_counter >= length:
                packet_counter = 0
                clear_buffers = False
        else:
            predicted_frequency = target_identification.handleFreqMessages(result, frequencies, expected_target, filter_by_comparison=True)
            if predicted_frequency is not None:
                clear_buffers = True
    target_identification.results.trialEnded(packet_count)
    result = target_identification.results.list[-1].getData(beta=0.2)
    print result
    # print result[c.RESULTS_DATA_TRUE_POSITIVES], result[c.RESULTS_DATA_FALSE_POSITIVES], result[c.RESULTS_DATA_MEAN_F1]
    return 1-result[c.RESULTS_DATA_MEAN_F1]


parameter_handler = NewTrainingParameterHandler()

# result = scipy.optimize.differential_evolution(
#     costFunction,
#     parameter_handler.getBounds(),
#     args=(parameter_handler, frequencies),
#     popsize=20,
#     seed=99,
#     disp=True
# )
# print result

# costFunction(
#     (0.5, 0.5, 0.5, 0.5, 1, 0.05, 0.05, 0.05, 0.1, 0.05, 1, 0.005),
#     parameter_handler,
#     frequencies
# )

# results = []
brute_force_parameter_handler = BruteForceHandler()
# for psda_1 in np.linspace(0, 0.2, num=10):
#     for psda_2 in np.linspace(0, 0.2, num=10):
#         for psda_3 in np.linspace(0, 0.2, num=10):
#             for psda_sum in np.linspace(0, 0.2, num=10):
#                 for cca in np.linspace(0, 0.2, num=10):
#                     minus_f1_score = costFunction(
#                         (psda_1, psda_2, psda_3, psda_sum, cca),
#                         brute_force_parameter_handler,
#                         frequencies
#                     )
#                     results.append(minus_f1_score)
#
# print counter
# print sorted(enumerate(results), key=lambda x: x[1])[1:100]
# 64100000
# np.linspace(0, 0.2, num=10)
# [(14601, 0.57058505242342306), (14611, 0.57216499885606542), (14500, 0.57346887064763219), (24600, 0.57428361051969412), (15600, 0.57453327628920636), (14700, 0.57465885003255601), (13600, 0.57480105718707442), (14701, 0.57563525003460092), (14610, 0.57651968156307132), (4600, 0.57669846869158525), (14501, 0.57705874395481294), (10501, 0.57708143223641017), (14711, 0.57718041861165825), (10601, 0.57776413860749964), (13700, 0.57807121902502612), (10701, 0.57836560180267016), (14620, 0.57842759041460612), (14650, 0.57859994837950257), (14511, 0.57862930990999351), (14400, 0.57877229190456547), (12600, 0.57886958455312509), (24500, 0.5792902795468764), (13601, 0.57929566343883399), (24610, 0.57976432314603044), (14661, 0.57981405004542586), (10511, 0.58000051225158356), (15610, 0.58013786483471086), (13701, 0.58024709029115473), (13650, 0.58029424673894492), (14640, 0.5803105600706131), (14520, 0.58041239034457459), (13611, 0.58068271228975776), (12601, 0.58069930139484116), (14550, 0.5807221691629969), (10611, 0.58073563229386749), (23600, 0.58075348424887618), (14630, 0.58084606699131469), (25600, 0.58095290425702917), (0, 0.58102070351226653), (14621, 0.58118791704751382), (10711, 0.58128341802110928), (12701, 0.58130273460956783), (14510, 0.58130300988447292), (24700, 0.58131780702960323), (15700, 0.58132228996418711), (4500, 0.58135050112976505), (13711, 0.5816036143263803), (15601, 0.58173384734338385), (13620, 0.58176255014433376), (30, 0.58188516467918672), (4601, 0.58188551356252394), (12700, 0.5818897405268938), (13661, 0.58213898102213224), (12611, 0.58216227994679626), (24620, 0.5821880559613466), (501, 0.5822297020423306), (14540, 0.5822551035916903), (15500, 0.58225629324836814), (14561, 0.58235044587098117), (4100, 0.58248533956211812), (14100, 0.58250463814946718), (13500, 0.58251594286874542), (13610, 0.58259399980323279), (24650, 0.5827043343048004), (12711, 0.58272987533414655), (100, 0.58275047200576113), (14530, 0.58275245410249243), (4700, 0.58286259956269437), (5600, 0.58287824826379386), (11511, 0.58309333042481915), (14710, 0.58313129353679205), (601, 0.58316307047144389), (24601, 0.58321752679511418), (14440, 0.58326971318706677), (11501, 0.58337909853585113), (14521, 0.58338352341983657), (12500, 0.58349259195217174), (10000, 0.58353289410732367), (14651, 0.5835621722562857), (4611, 0.58357696321680108), (15611, 0.58358149987767516), (13640, 0.5836613346176025), (3600, 0.58374910730546292), (25610, 0.58378950221316517), (15620, 0.58379206440804876), (13761, 0.58380738492713014), (701, 0.58391715737279393), (10521, 0.58396586336978507), (11611, 0.58398811493972302), (14641, 0.58401093172024232), (15650, 0.58401594473327378), (12620, 0.58412259845451664), (24520, 0.58412766108612324), (13630, 0.58415868512840463), (13750, 0.58416468941721678), (14800, 0.58419264167079099), (24640, 0.58419931916413903), (11601, 0.58436865140711314), (23650, 0.5843891504566453)]

costFunction(
    (0.025, 0.09, 0.135, 0.01, 0.02),
    brute_force_parameter_handler,
    frequencies
)
