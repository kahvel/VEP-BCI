__author__ = 'Anti'

import random
import constants as c
from connections import MasterConnection, ConnectionPostOfficeEnd
import winsound
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
        self.need_new_target = None
        self.message_counter = None
        self.waitConnections()

    def waitConnections(self):
        setup_successful = False
        message = None
        while True:
            if message is not None:
                if message == c.START_MESSAGE:
                    if setup_successful:
                        message = self.start()
                        continue
                    else:
                        print("Setup was not successful!")
                elif message == c.SETUP_MESSAGE:
                    if self.setup() == c.SUCCESS_MESSAGE:
                        setup_successful = True
                        print("Setup successful!")
                    else:
                        setup_successful = False
                        print("Setup failed!")
                elif message == c.STOP_MESSAGE:
                    print("Stop PostOffice")
                elif message == c.RESET_RESULTS_MESSAGE:
                    self.results.reset()
                elif message == c.SHOW_RESULTS_MESSAGE:
                    print(self.results)
                elif message == c.SAVE_RESULTS_MESSAGE:
                    self.results.save()
                elif message == c.EXIT_MESSAGE:
                    self.exit()
                    return
                else:
                    print("Unknown message in PostOffice: " + str(message))
            message = self.main_connection.receiveMessagePoll(0.1)

    def countFreqs(self, freqs, cca=False):
        result = {}
        for tab in freqs:
            if freqs[tab] not in result:
                result[freqs[tab]] = 1 if cca is False else 1
            else:
                result[freqs[tab]] += 1 if cca is False else 1
        return result

    def countAllFreqs(self, *freqs_dicts):
        result = {}
        for dict in freqs_dicts:
            for freq in dict:
                if round(freq, 2) not in result:
                    result[round(freq, 2)] = dict[freq]
                else:
                    result[round(freq, 2)] += dict[freq]
        return result

    def getResults(self, results, current_target, method):
        wrong = []
        correct = []
        all_results, max_freqs = results[:2]
        if max_freqs != {}:
            freq = max_freqs.values()[0]
            if freq == current_target:
                correct.append((method, freq))
            else:
                wrong.append((method, freq))
        return correct, wrong

    def getSumPsdaResults(self, results, current_target, method):
        return {key: self.getResults(results[key], current_target, method) for key in results}

    def getPsdaResults(self, results, current_target, method):
        return {key: self.getSumPsdaResults(results[key], current_target, method) for key in results}

    def findCorrectResults(self, results, target_freqs):
        result = self.countAllFreqs(
            self.countFreqs(results[c.CCA][1], cca=True),
            # self.countFreqs(results[c.SUM_PSDA][1][1] if 1 in results[c.SUM_PSDA] else {}),
            # self.countFreqs(results[c.SUM_PSDA][2][1] if 2 in results[c.SUM_PSDA] else {}),
            # self.countFreqs(results[c.SUM_PSDA][3][1] if 3 in results[c.SUM_PSDA] else {}),
            self.countFreqs(results[c.SUM_PSDA][c.RESULT_SUM][1] if c.RESULT_SUM in results[c.SUM_PSDA] else {}),
            # self.countFreqs(results[c.PSDA]["O1"][1][1] if "O1" in results[c.PSDA] and 1 in results[c.PSDA]["O1"] else {}),
            # self.countFreqs(results[c.PSDA]["O1"][2][1] if "O1" in results[c.PSDA] and 2 in results[c.PSDA]["O1"] else {}),
            # self.countFreqs(results[c.PSDA]["O1"][3][1] if "O1" in results[c.PSDA] and 3 in results[c.PSDA]["O1"] else {}),
            # self.countFreqs(results[c.PSDA]["O1"][c.RESULT_SUM][1] if "O1" in results[c.PSDA] and c.RESULT_SUM in results[c.PSDA]["O1"] else {}),
            # self.countFreqs(results[c.PSDA]["O2"][1][1] if "O2" in results[c.PSDA] and 1 in results[c.PSDA]["O2"] else {}),
            # self.countFreqs(results[c.PSDA]["O2"][2][1] if "O2" in results[c.PSDA] and 2 in results[c.PSDA]["O2"] else {}),
            # self.countFreqs(results[c.PSDA]["O2"][3][1] if "O2" in results[c.PSDA] and 3 in results[c.PSDA]["O2"] else {}),
            # self.countFreqs(results[c.PSDA]["O2"][c.RESULT_SUM][1] if "O2" in results[c.PSDA] and c.RESULT_SUM in results[c.PSDA]["O2"] else {}),
            # self.countFreqs(results[c.PSDA][c.RESULT_SUM][1][1] if c.RESULT_SUM in results[c.PSDA] and 1 in results[c.PSDA][c.RESULT_SUM] else {}),
            # self.countFreqs(results[c.PSDA][c.RESULT_SUM][2][1] if c.RESULT_SUM in results[c.PSDA] and 2 in results[c.PSDA][c.RESULT_SUM] else {}),
            # self.countFreqs(results[c.PSDA][c.RESULT_SUM][3][1] if c.RESULT_SUM in results[c.PSDA] and 3 in results[c.PSDA][c.RESULT_SUM] else {}),
            self.countFreqs(results[c.PSDA][c.RESULT_SUM][c.RESULT_SUM][1] if c.RESULT_SUM in results[c.PSDA] and c.RESULT_SUM in results[c.PSDA][c.RESULT_SUM] else {}),
        )
        for freq in target_freqs:
            if round(freq, 2) not in result:
                result[round(freq, 2)] = 0
        return result

    def handleFreqMessages(self, message, target_freqs, current_target):
        results = message
        rounded_target_freqs = tuple(round(freq, 2) for freq in target_freqs)
        if results is not None:
            counted_freqs = self.findCorrectResults(results, target_freqs)
            max_freq_rounded, max_count = max(counted_freqs.items(), key=lambda x: x[1])
            max_freq = target_freqs[rounded_target_freqs.index(max_freq_rounded)]
            if max_count >= sum(counted_freqs.values()):
                self.prev_results.append(max_freq)
                self.prev_results_counter[max_freq] += 1
                if len(self.prev_results) > 1:
                    self.prev_results_counter[self.prev_results[0]] -= 1
                    del self.prev_results[0]
                f, m = max(self.prev_results_counter.items(), key=lambda x: x[1])
                max_freq = f
                if m >= 1:
                    if max_freq == self.standby_freq:
                        # self.connections.sendPlotMessage(self.standby_state and not self.no_standby)
                        self.standby_state = not self.standby_state
                        self.connections.sendTargetMessage(self.standby_state)
                        winsound.Beep(2500, 100)
                        self.prev_results = []
                    if not self.standby_state or self.no_standby:
                        self.connections.sendTargetMessage(max_freq)
                        # self.connections.sendGameMessage(max_freq)
                        if not self.results.isPrevResult(max_freq):
                            self.results.addResult(target_freqs[current_target-1], max_freq)
                            if max_freq != target_freqs[current_target-1]:
                                print(counted_freqs, max_freq_rounded, max_count, target_freqs[current_target-1], self.prev_results)
                        if max_freq == target_freqs[current_target-1]:
                            self.need_new_target = True

    def getTotalTime(self, unlimited, test_time):
        return float("inf") if unlimited else test_time

    def getTarget(self, test_target, target_count):
        if self.isRandom(test_target):
            return random.randint(1, target_count)
        elif test_target != c.TEST_NONE:
            return test_target
        else:
            return None

    def isRandom(self, test_target):
        return test_target == c.TEST_RANDOM

    def targetChangingLoop(self, options, target_freqs):
        total_time = self.getTotalTime(options[c.TEST_UNLIMITED], options[c.TEST_TIME])
        while self.message_counter < total_time:
            target = self.getTarget(options[c.TEST_TARGET], len(target_freqs))
            if target is not None:
                self.connections.sendTargetMessage(target)
            self.need_new_target = False
            message = self.startPacketSending(target_freqs, target, total_time)
            if message is not None:
                return message
        self.main_connection.sendMessage(c.STOP_MESSAGE)

    def setStandby(self, options):
        if self.isStandby(options[c.DATA_TEST][c.TEST_STANDBY]):
            self.no_standby = False
            self.standby_freq = options[c.DATA_FREQS][options[c.DATA_TEST][c.TEST_STANDBY]-1]
        else:
            self.no_standby = True
        self.standby_state = False

    def setup(self):
        self.options = self.main_connection.receiveMessageBlock()
        self.connections.setup(self.options)
        self.setStandby(self.options)
        self.message_counter = 0
        self.prev_results = []
        self.prev_results_counter = {freq: 0 for freq in self.options[c.DATA_FREQS]}
        if self.connections.setupSuccessful():
            self.results.setup(self.options[c.DATA_FREQS])
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
        self.connections.sendStartMessage()
        message = self.targetChangingLoop(
            self.options[c.DATA_TEST],
            self.options[c.DATA_FREQS],
        )
        self.results.trialEnded(self.message_counter)
        self.message_counter = 0
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

    def startPacketSending(self, target_freqs, current_target, total_time):
        while not self.need_new_target and self.message_counter < total_time:
            main_message = self.main_connection.receiveMessageInstant()
            if main_message is not None:
                return main_message
            self.handleEmotivMessages(target_freqs, current_target)
