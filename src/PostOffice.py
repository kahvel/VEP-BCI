import random

import constants as c
from connections import MasterConnection, ConnectionPostOfficeEnd
import Results


class PostOffice(object):
    def __init__(self):
        self.main_connection = ConnectionPostOfficeEnd.MainConnection()
        self.connections = MasterConnection.MasterConnection()
        self.options = None
        self.results = Results.Results()
        self.standby_state = None
        self.standby_freq = None
        self.no_standby = None
        self.recorded_signals = [None for _ in range(7)]
        self.prev_results = []
        self.prev_results_counter = {}
        self.actual_results = []
        self.actual_results_counter = {}
        self.need_new_target = None
        self.new_target_counter = None
        self.message_counter = None
        self.differences = []
        self.waitConnections()

    def waitConnections(self):
        message = None
        while True:
            if message is not None:
                if message == c.START_MESSAGE:
                    message = self.start()
                    continue
                elif message == c.SETUP_MESSAGE:
                    setup_message = self.setup()
                    if setup_message == c.FAIL_MESSAGE:
                        self.connections.close()
                    print("Setup " + setup_message + "!")
                    self.main_connection.sendMessage(setup_message)
                elif message == c.STOP_MESSAGE:
                    print("Stop PostOffice")
                elif message == c.RESET_RESULTS_MESSAGE:
                    self.results.reset()
                elif message == c.SHOW_RESULTS_MESSAGE:
                    print(self.results)
                elif message == c.SAVE_RESULTS_MESSAGE:
                    self.results.askSaveFile()
                elif message == c.EXIT_MESSAGE:
                    self.exit()
                    return
                elif message in c.ROBOT_COMMANDS:
                    self.connections.sendRobotMessage(message)
                else:
                    print("Unknown message in PostOffice: " + str(message))
            message = self.main_connection.receiveMessagePoll(0.1)

    def countCca(self, counted_freqs, results, weight):
        counted_freqs[round(results[0][0], 2)] += weight
        self.differences.append(results[0][1]-results[1][1])

    def countSumPsda(self, counted_freqs, results, weight):
        for harmonic in results:
            if harmonic in weight:
                self.countCca(counted_freqs, results[harmonic], weight[harmonic])

    def countPsda(self, counted_freqs, results, weight):
        for sensor in results:
            if sensor in weight:
                self.countSumPsda(counted_freqs, results[sensor], weight[sensor])

    def countAll(self, results, target_freqs, weight):
        counted_results = {round(freq, 2): 0 for freq in target_freqs}
        for tab in results:
            for method in results[tab]:
                if tab in weight and method[0] in weight[tab]:
                    if method[0] == c.CCA:
                        self.countCca(counted_results, results[tab][method], weight[tab][method[0]])
                    elif method[0] == c.SUM_PSDA:
                        self.countSumPsda(counted_results, results[tab][method], weight[tab][method[0]])
                    elif method[0] == c.PSDA:
                        self.countPsda(counted_results, results[tab][method], weight[tab][method[0]])
        return counted_results

    def getDictKey(self, dict, value_arg):
        for key, value in dict.items():
            if value == value_arg:
                return key

    def handleFreqMessages(self, message, target_freqs, current_target):
        results = message
        target_freqs_dict = target_freqs
        target_freqs = target_freqs_dict.values()
        rounded_target_freqs = tuple(round(freq, 2) for freq in target_freqs)
        if results is not None:
            self.differences = []
            counted_freqs = self.countAll(results, target_freqs, {6: {c.CCA: 1}, 5: {c.SUM_PSDA: {1.0: 0.5, c.RESULT_SUM: 0.5}}})
            if all(map(lambda x: x > 0.1, self.differences)):
                for freq in counted_freqs:
                    self.prev_results_counter[freq] += counted_freqs[freq]
                self.prev_results.append(counted_freqs)
                if len(self.prev_results) > 1:
                    for result in self.prev_results[0]:
                        self.prev_results_counter[result] -= self.prev_results[0][result]
                    del self.prev_results[0]
                    f, m = max(self.prev_results_counter.items(), key=lambda x: x[1])
                    if m >= 1.5:
                        self.actual_results.append(f)
                        self.actual_results_counter[f] += 1
                        if len(self.actual_results) > 1:
                            self.actual_results_counter[self.actual_results[0]] -= 1
                            del self.actual_results[0]
                            f1, m1 = max(self.actual_results_counter.items(), key=lambda x: x[1])
                            max_freq = target_freqs[rounded_target_freqs.index(f1)]
                            if m1 >= 1:
                                # if max_freq == self.standby_freq:
                                #     # self.connections.sendPlotMessage(self.standby_state and not self.no_standby)
                                #     self.standby_state = not self.standby_state
                                #     self.connections.sendTargetMessage(self.standby_state)
                                #     winsound.Beep(2500, 100)
                                #     self.prev_results = []
                                if not self.standby_state or self.no_standby:
                                    self.connections.sendTargetMessage(max_freq)
                                    current = target_freqs_dict[current_target] if current_target in target_freqs_dict else None
                                    if not self.results.isPrevResult(max_freq):
                                        self.results.addResult(current, max_freq)
                                        self.connections.sendRobotMessage(self.getDictKey(target_freqs_dict, max_freq))
                                        print(self.differences, sum(self.differences))
                                        if max_freq != current:
                                            print("wrong", self.actual_results, self.actual_results_counter, self.prev_results_counter, current, f1)
                                        else:
                                            print("right", self.actual_results, self.actual_results_counter, self.prev_results_counter, current, f1)
                                    if max_freq == current:
                                        self.new_target_counter += 1
                                        if self.new_target_counter > 0:
                                            self.need_new_target = True
                                            self.new_target_counter = 0

    def getTotalTime(self, unlimited, test_time):
        return float("inf") if unlimited else test_time

    def getTarget(self, test_target, target_freqs, previous_target):
        if self.isRandom(test_target):
            targets = target_freqs.keys()
            if previous_target is not None and len(targets) > 1:
                targets.remove(previous_target)
            return random.choice(targets)
        elif test_target != c.TEST_NONE:
            return test_target
        else:
            return None

    def isRandom(self, test_target):
        return test_target == c.TEST_RANDOM

    def targetChangingLoop(self, options, target_freqs):
        total_time = self.getTotalTime(options[c.TEST_UNLIMITED], options[c.TEST_TIME])
        target = None
        while self.message_counter < total_time:
            target = self.getTarget(options[c.TEST_TARGET], target_freqs, target)
            if target is not None:
                self.connections.sendTargetMessage(target)
            self.need_new_target = False
            self.new_target_counter = 0
            message = self.startPacketSending(target_freqs, target, total_time)
            if message is not None:
                return message
        self.main_connection.sendMessage(c.STOP_MESSAGE)
        return c.STOP_MESSAGE

    def setStandby(self, options):
        if self.isStandby(options[c.DATA_TEST][c.TEST_STANDBY]):
            self.no_standby = False
            self.standby_freq = options[c.DATA_FREQS][options[c.DATA_TEST][c.TEST_STANDBY]]
        else:
            self.no_standby = True
        self.standby_state = False

    def setup(self):
        self.options = self.main_connection.receiveMessageBlock()
        self.connections.setup(self.options)
        self.setStandby(self.options)
        if self.connections.setupSuccessful():
            self.results.setup(self.options[c.DATA_FREQS].values())
            return c.SUCCESS_MESSAGE
        else:
            return c.FAIL_MESSAGE

    def exit(self):
        self.connections.close()
        self.main_connection.close()

    def isStandby(self, standby):
        if standby == c.TEST_NONE:
            return False
        else:
            return True

    def start(self):
        self.prev_results = []
        self.actual_results = []
        rounded_target_freqs = tuple(round(freq, 2) for freq in self.options[c.DATA_FREQS].values())
        self.prev_results_counter = {freq: 0 for freq in rounded_target_freqs}
        self.actual_results_counter = {freq: 0 for freq in rounded_target_freqs}
        self.message_counter = 0
        self.connections.sendStartMessage()
        message = self.targetChangingLoop(
            self.options[c.DATA_TEST],
            self.options[c.DATA_FREQS],
        )
        self.results.trialEnded(self.message_counter)
        self.connections.sendStopMessage()
        return message

    def handleEmotivMessages(self, target_freqs, current_target):
        message = self.connections.receiveEmotivMessage()
        if message is not None:
            self.message_counter += 1
            self.connections.sendExtractionMessage(message)
            self.connections.sendPlotMessage(message)
            self.handleFreqMessages(
                self.connections.receiveExtractionMessage(),
                target_freqs,
                current_target
            )

    def handleRobotMessages(self):
        message = self.connections.receiveRobotMessage()
        if message is not None:
            self.connections.sendTargetMessage(message)

    def startPacketSending(self, target_freqs, current_target, total_time):
        while not self.need_new_target and self.message_counter < total_time:
            main_message = self.main_connection.receiveMessageInstant()
            if main_message in c.ROBOT_COMMANDS:
                self.connections.sendRobotMessage(main_message)
            elif main_message is not None:
                return main_message
            self.handleEmotivMessages(target_freqs, current_target)
            self.handleRobotMessages()
