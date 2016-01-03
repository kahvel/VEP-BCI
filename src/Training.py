import constants as c
import BCI
import ParameterHandler
import TargetIdentification

import copy
import os


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

    def differentialEvolution(self, options):
        pass

    def bruteForce(self, options):
        options_generator = ParameterHandler.BruteForce().optionsGenerator()
        import time
        start = time.time()
        counter = 0
        for signal_processing_options in options_generator:
            self.expected_target_index = 0
            self.result = 0
            file_name = "C:\\Users\\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\src\\results\\_" + str(counter) + ".txt"
            self.results_file = open(file_name, "w")
            self.results_file.write(str(signal_processing_options) + "\n")
            for tab in options[c.DATA_EXTRACTION]:
                options[c.DATA_EXTRACTION][tab][c.DATA_EXTRACTION_OPTIONS] = signal_processing_options
            BCI.BCI.setup(self, options)
            BCI.BCI.start(self, options)
            self.results_file.write(str(self.result))
            self.results_file.close()
            # os.rename(file_name, file_name[:58] + str(self.result) + file_name[58:])
            counter += 1
        print time.time() - start, counter

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

    def handleExtractionMessages(self, target_freqs, current_target):
        results = self.connections.receiveExtractionMessage()
        if results is not None:
            self.results_file.write(str(results) + "\n")
            added = self.result_finder.parseResults(results)
            current = target_freqs[current_target]
            print added, current
            for freq in added:
                if freq == current:
                    self.result -= added[freq]
                else:
                    self.result += added[freq]


class ResultAdder(TargetIdentification.WeightFinder):
    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) != 0:
            if result[0][0] in parse_result:
                parse_result[result[0][0]] += result[0][1]
            else:
                parse_result[result[0][0]] = result[0][1]
