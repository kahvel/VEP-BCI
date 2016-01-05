import constants as c
import BCI
import ParameterHandler
import TargetIdentification

import copy
import os
import scipy.optimize


class Training(BCI.BCI):
    def __init__(self, connections, main_connection, recording):
        BCI.BCI.__init__(self, connections, main_connection, recording)
        self.packets = []
        self.expected_targets = []
        self.expected_target_index = 0
        self.target_freqs = {}
        # self.difference_finder = TargetIdentification.DifferenceFinder()
        # self.weight_finder = TargetIdentification.WeightFinder()
        self.result_finder = ResultAdder()
        self.result = 0
        self.results_file = None

    def setupPackets(self):  # Currently uses always first data entry in the lists
        self.packets = self.recording.normal_eeg.list[0][c.EEG_RECORDING_PACKETS]
        self.target_freqs = self.recording.normal_eeg.list[0][c.EEG_RECORDING_FREQS]
        self.expected_targets = self.recording.expected_targets.list[0]
        self.expected_target_index = 0

    def setupResultsParsers(self, options):
        # self.difference_finder.setup(options[c.DATA_EXTRACTION_DIFFERENCES])
        # self.weight_finder.setup(options[c.DATA_EXTRACTION_WEIGHTS])
        self.result_finder.setup(options[c.DATA_EXTRACTION_WEIGHTS])

    def setup(self, options):
        self.setupPackets()
        self.setupResultsParsers(options)
        return BCI.BCI.setup(self, self.changeOptions(options))

    def start(self, options):
        method = options[c.DATA_TRAINING][c.TRAINING_METHOD]
        if method == c.TRAINING_METHOD_SINGLE:
            return BCI.BCI.start(self, self.changeOptions(options))
        elif method == c.TRAINING_METHOD_DE:
            return self.differentialEvolution(self.changeOptions(options))
        elif method == c.TRAINING_METHOD_BRUTE_FORCE:
            return self.bruteForce(self.changeOptions(options))
        elif method == c.TRAINING_METHOD_DE_IDENTIFICATION:
            return self.differentialEvolutionIdentification(self.changeOptions(options))

    def differentialEvolutionIdentification(self, options):
        self.options_handler = ParameterHandler.DifferentialEvolutionIdentification()
        self.counter = 1
        self.directory = "C:\\Users\\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\src\\results_de_i\\dummy\\"
        f = open(self.directory + "options.txt", "w")
        f.write(str(options))
        f.close()
        # For timing cost function evaluation
        # self.differentialEvolutionIdentificationCostFunction((1,1,1,1,1,0.1,0.1,0.1,0.1,0.1,1,3), self.options_handler, options)
        scipy.optimize.differential_evolution(
            self.differentialEvolutionIdentificationCostFunction,
            self.options_handler.getBounds(),
            args=(self.options_handler, options),
        )

    def differentialEvolutionIdentificationCostFunction(self, numbers, options_handler, all_options):
        self.expected_target_index = 0
        new_options = options_handler.numbersToOptions(numbers)
        all_options[c.DATA_EXTRACTION_WEIGHTS] = new_options[c.DATA_EXTRACTION_WEIGHTS]
        all_options[c.DATA_EXTRACTION_DIFFERENCES] = new_options[c.DATA_EXTRACTION_DIFFERENCES]
        # new_options[c.DATA_ACTUAL_RESULTS][c.DATA_ALWAYS_DELETE] = all_options[c.DATA_ACTUAL_RESULTS][c.DATA_ALWAYS_DELETE]
        new_options[c.DATA_PREV_RESULTS][c.DATA_ALWAYS_DELETE] = all_options[c.DATA_PREV_RESULTS][c.DATA_ALWAYS_DELETE]
        # all_options[c.DATA_ACTUAL_RESULTS] = new_options[c.DATA_ACTUAL_RESULTS]
        all_options[c.DATA_PREV_RESULTS] = new_options[c.DATA_PREV_RESULTS]
        BCI.BCI.setup(self, all_options)
        BCI.BCI.start(self, all_options)
        result = self.target_identification.results.list[-1]["Wrong"] - self.target_identification.results.list[-1]["Correct"]
        f = open(self.directory + str(self.counter) + ".txt", "w")
        f.write(str(new_options) + "\n")
        f.write(str(result))
        f.close()
        self.counter += 1
        return result

    def differentialEvolution(self, options):
        self.options_handler = ParameterHandler.DifferentialEvolution()
        self.all_results = {}
        scipy.optimize.differential_evolution(
            self.differentialEvolutionCostFunction,
            self.options_handler.getBounds(),
            args=(self.options_handler, options),
            popsize=3,
            callback=self.differentialEvolutionCallback,
        )

    def differentialEvolutionCallback(self, x, convergence=None):
        signal_processing_options = self.options_handler.numbersToOptions(x)
        print "callback", signal_processing_options, self.all_results[str(" ".join(str(signal_processing_options[key]) for key in sorted(signal_processing_options)))]

    def differentialEvolutionCostFunction(self, numbers, options_handler, all_options):
        signal_processing_options = options_handler.numbersToOptions(numbers)
        return self.costFunction(all_options, signal_processing_options)

    def costFunction(self, options, signal_processing_options):
        self.expected_target_index = 0
        self.result = 0
        for tab in options[c.DATA_EXTRACTION]:
            options[c.DATA_EXTRACTION][tab][c.DATA_EXTRACTION_OPTIONS] = copy.deepcopy(signal_processing_options)
        options[c.DATA_EXTRACTION][2][c.DATA_EXTRACTION_OPTIONS][c.OPTIONS_WINDOW] = c.WINDOW_NONE
        BCI.BCI.setup(self, options)
        BCI.BCI.start(self, options)
        self.result *= signal_processing_options[c.OPTIONS_STEP]
        self.all_results[str(" ".join(str(signal_processing_options[key]) for key in sorted(signal_processing_options)))] = self.result
        print signal_processing_options, self.result
        return self.result

    def bruteForce(self, options):
        options_generator = ParameterHandler.BruteForce().optionsGenerator()
        counter = 0
        for signal_processing_options in options_generator:
            file_name = "C:\\Users\\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\src\\results1\\_" + str(counter) + ".txt"
            self.results_file = open(file_name, "w")
            self.results_file.write(str(signal_processing_options) + "\n")
            result = self.costFunction(options, signal_processing_options)
            self.results_file.write(str(result))
            self.results_file.close()
            counter += 1

    def changeOptions(self, options):
        options = copy.deepcopy(options)
        self.disableUnnecessaryOptions(options)
        self.setTrainingTime(options)
        self.fixFrequencies(options)
        return options

    def fixFrequencies(self, options):
        options[c.DATA_FREQS] = self.target_freqs
        for tab in options[c.DATA_EXTRACTION]:
            options[c.DATA_EXTRACTION][tab][c.DATA_EXTRACTION_TARGETS] = self.target_freqs  # TODO allow disabling

    def disableUnnecessaryOptions(self, options):
        options[c.DATA_RECORD][c.TRAINING_RECORD] = c.TRAINING_RECORD_DISABLED
        options[c.DATA_TEST][c.TEST_STANDBY] = c.TEST_NONE
        options[c.DATA_BACKGROUND] = {c.DISABLE: 1}
        options[c.DATA_ROBOT] = {c.DISABLE: 1}
        options[c.DATA_EMOTIV] = {c.DISABLE: 1}
        options[c.DATA_PLOTS] = {}

    def setTrainingTime(self, options):
        options[c.DATA_TEST][c.TEST_UNLIMITED] = False
        options[c.DATA_TEST][c.TEST_TIME] = self.getTotalTrainingTime()

    def getTotalTrainingTime(self):
        return len(self.packets)

    def getTarget(self, test_target, target_freqs, previous_target):
        if self.expected_target_index < len(self.expected_targets):
            if self.expected_targets[self.expected_target_index][1] == self.message_counter:
                self.expected_target_index += 1
                return self.expected_targets[self.expected_target_index-1][0]
        return previous_target

    def getNextPacket(self):
        return self.packets[self.message_counter]

    def startPacketSending(self, target_freqs, current_target, total_time):
        while not self.target_identification.need_new_target and self.message_counter < total_time:
            main_message = self.main_connection.receiveMessageInstant()
            if main_message in c.ROBOT_COMMANDS:
                self.connections.sendRobotMessage(main_message)
            elif main_message is not None:
                print main_message + "!!!"
                return main_message
            current_target = self.getTarget(None, None, current_target)  # Override for this line
            self.handleEmotivMessages(target_freqs, current_target)

    # def handleExtractionMessages(self, target_freqs, current_target):  # for brute force and DE
    #     results = self.connections.receiveExtractionMessage()
    #     if results is not None:
    #         # self.results_file.write(str(results) + "\n")
    #         added = self.result_finder.parseResults(results)
    #         current = target_freqs[current_target]
    #         for freq in added:
    #             if freq == current:
    #                 self.result -= added[freq]
    #             else:
    #                 self.result += added[freq]


class ResultAdder(TargetIdentification.WeightFinder):
    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) != 0:
            if result[0][0] in parse_result:
                parse_result[result[0][0]] += result[0][1] * data
            else:
                parse_result[result[0][0]] = result[0][1] * data
