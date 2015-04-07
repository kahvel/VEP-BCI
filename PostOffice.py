__author__ = 'Anti'

import multiprocessing.reduction
import random
import numpy as np
import constants as c
from connections import ConnectionPostOfficeEnd


class PostOffice(object):
    def __init__(self):
        self.main_connection = ConnectionPostOfficeEnd.MainConnection()
        self.connections = {
            c.CONNECTION_EMOTIV:     ConnectionPostOfficeEnd.EmotivConnection(),
            c.CONNECTION_PSYCHOPY:   ConnectionPostOfficeEnd.PsychopyConnection(),
            c.CONNECTION_EXTRACTION: ConnectionPostOfficeEnd.MultipleExtractionConnections(),
            c.CONNECTION_PLOT:       ConnectionPostOfficeEnd.MultiplePlotConnections(),
            c.CONNECTION_GAME:       ConnectionPostOfficeEnd.GameConnection()
        }
        """
        @type : dict[str, ConnectionPostOfficeEnd.Connection | ConnectionPostOfficeEnd.MultipleConnections]
        """
        self.connection_options_key = {
            c.CONNECTION_EXTRACTION: c.DATA_EXTRACTION,
            c.CONNECTION_PLOT: c.DATA_PLOTS,
        }
        self.results = None
        self.resetResults()
        self.standby = None
        self.standby_freq = None
        self.recorded_signals = [None for _ in range(7)]
        self.waitConnections()

    def addConnection(self, connections_list, title):
        print "Adding pipe to", title
        connection = multiprocessing.reduction.rebuild_pipe_connection(*self.main_connection.recv()[1])
        connections_list.append(connection)

    def waitConnections(self):
        while True:
            message = self.main_connection.receiveMessagePoll(0.1)
            if message is not None:
                if message == "Add emotiv":
                    self.addConnection(self.emotiv_connection, "emotiv")
                elif message == "Add psychopy":
                    self.addConnection(self.psychopy_connection, "psychopy")
                elif message == "Add plot":
                    self.addConnection(self.plot_connection, "plot")
                elif message == "Add extraction":
                    self.addConnection(self.extraction_connection, "extraction")
                elif message == "Add game":
                    self.addConnection(self.game_connection, "game")
                elif message == c.START_MESSAGE:
                    self.start()
                elif message == "Threshold":
                    self.calculateThreshold()
                elif message == c.EXIT_MESSAGE:
                    self.sendMessage(self.emotiv_connection, c.EXIT_MESSAGE)
                    self.sendMessage(self.psychopy_connection, c.EXIT_MESSAGE)
                    self.sendMessage(self.plot_connection, c.EXIT_MESSAGE)
                    self.sendMessage(self.extraction_connection, c.EXIT_MESSAGE)
                    self.sendMessage(self.game_connection, c.EXIT_MESSAGE)
                    while True:  # wait until all connections are closed
                        self.getMessages(self.psychopy_connection, "Psychopy")
                        self.getMessages(self.plot_connection, "Plot")
                        self.getMessages(self.extraction_connection, "Extraction")
                        self.getMessages(self.game_connection, "Game")
                        if len(self.psychopy_connection)+len(self.plot_connection)+len(self.extraction_connection) == 0:
                            return
                elif message == "Record neutral":
                    self.sendMessage(self.emotiv_connection, "Start")
                    self.recordSignal(self.main_connection.recv(), self.main_connection.recv())
                    self.sendMessage(self.emotiv_connection, "Stop")
                elif message == "Record target":
                    self.sendMessage(self.psychopy_connection, "Start")
                    self.sendMessage(self.psychopy_connection, self.main_connection.recv())
                    self.sendMessage(self.psychopy_connection, self.main_connection.recv())
                    self.sendMessage(self.emotiv_connection, "Start")
                    self.recordSignal(self.main_connection.recv(), self.main_connection.recv())
                    self.sendMessage(self.emotiv_connection, "Stop")
                    self.sendMessage(self.psychopy_connection, "Stop")
                elif message == "Reset results":
                    self.resetResults()
                elif message == "Show results":
                    self.printResults()
                else:
                    print "Unknown message:", message

    def calculateThreshold(self):
        target_freqs = self.main_connection.recv()
        all_results = []
        for signal in self.recorded_signals:
            if signal is not None:
                self.sendMessage(self.extraction_connection, "Start")
                self.sendMessage(self.extraction_connection, target_freqs)
                for packet in signal:
                    self.sendMessage(self.extraction_connection, packet)
                self.sendMessage(self.extraction_connection, "Stop")
                self.sendMessage(self.extraction_connection, "Results")
                while True:
                    if "Results" in self.getMessages(self.extraction_connection, "Extraction", poll=lambda connection: True):
                        break
                all_results.append(self.getMessages(self.extraction_connection, "Extraction", poll=lambda connection: True))
            else:
                all_results.append(None)
        shaped_results = []
        print "results", all_results
        index = 0
        for i in range(len(all_results)):  # target
            if all_results[i] is not None:
                for window in range(len(all_results[i])):  # window
                    if len(shaped_results) != len(all_results[i]):
                        shaped_results.append({})
                    for method in all_results[i][window]:  # method
                        print method
                        transposed_result = np.transpose(all_results[i][window][method])
                        if method not in shaped_results[window]:
                            shaped_results[window][method] = {True:  [[] for _ in range(len(transposed_result))],
                                                  False: [[] for _ in range(len(transposed_result))]}
                        for target in range(len(transposed_result)):  # target
                            if index == 0:
                                shaped_results[window][method][False][target] = np.append(shaped_results[window][method][False][target], transposed_result[target][16:], 1)
                            elif index-1 == target:
                                shaped_results[window][method][True][target] = np.append(shaped_results[window][method][True][target], transposed_result[target][16:], 1)
                            else:
                                shaped_results[window][method][False][target] = np.append(shaped_results[window][method][False][target], transposed_result[target][16:], 1)
                            print transposed_result[target]
                index += 1
        print shaped_results
        thresholds = []
        for window in shaped_results:
            thresholds.append({})
            for method in window:
                thresholds[-1][method] = {}
                for boolean in window[method]:
                    thresholds[-1][method][boolean] = []
                    for target in window[method][boolean]:
                        thresholds[-1][method][boolean].append([])
                        if len(target) != 0:
                            thresholds[-1][method][boolean][-1].append(min(target))
                            thresholds[-1][method][boolean][-1].append(sum(target)/len(target))
                            thresholds[-1][method][boolean][-1].append(max(target))
        print thresholds

    def recordSignal(self, length, target_n):
        signal = []
        while len(signal) < length:
            if self.main_connection.poll():
                message = self.main_connection.recv()
                return message
            if self.emotiv_connection[0].poll():
                message = self.emotiv_connection[0].recv()
                signal.append(message)
        self.recorded_signals[target_n] = signal

    def getMessages(self, connections, name, poll=lambda connection: connection.poll()):
        ret = []
        for i in range(len(connections)-1, -1, -1):
            if poll(connections[i]):
                message = connections[i].recv()
                if message == "Close":
                    print name, "pipe closed"
                    connections[i].close()
                    del connections[i]
                elif isinstance(message, tuple):  # elif name == "Extraction" and isinstance(message, float):
                    ret.append(message)
                else:  # elif isinstanse(message, list)
                    ret.append(message)
        return ret

    def handleFreqMessages(self, messages, no_standby, target_freqs, current_target):
        for result in messages:
            if result is not None:
                for freq, class_name in result:
                    self.results[class_name][str(target_freqs)][current_target][freq] += 1
                    if freq == self.standby_freq:
                        self.sendMessage(self.psychopy_connection, self.standby and not no_standby)
                        self.standby = not self.standby
                    if not self.standby or no_standby:
                        if not "short" in class_name:
                            self.sendMessage(self.psychopy_connection, freq)
                            self.sendMessage(self.game_connection, freq)

    def sendMessage(self, connections, message):
        for i in range(len(connections)-1, -1, -1):
            connections[i].send(message)

    def randomSequence(self, total, min_value, max_value, target_freqs):
        data = []
        initial_values = {i: total for i in range(len(target_freqs))}
        while True:
            target = random.choice(initial_values.keys())
            time = random.randint(min_value, max_value)
            if initial_values[target] - time < min_value:
                time = initial_values[target]
            initial_values[target] = initial_values[target]-time
            if len(data) > 0 and data[-1][0] == target:
                data[-1][1] += time
            else:
                data.append([target, time])
            if initial_values[target] == 0:
                del initial_values[target]
                if initial_values == {}:
                    break
        return data

    def normalSequence(self, target, time):
        return [[target, time]]

    def getSequence(self, options):
        if options[c.TEST_TARGET] == c.TEST_RANDOM:
            return self.randomSequence(options[c.TEST_TIME], options[c.TEST_MIN], options[c.TEST_MAX], options[c.DATA_FREQS])
        elif c.TEST_UNLIMITED:
            return self.normalSequence(options[c.TEST_TARGET], float("inf"))
        else:
            return self.normalSequence(options[c.TEST_TARGET], options[c.TEST_TIME])

    def resetResults(self):
        self.results = {name: {} for name in c.EXTRACTION_METHOD_NAMES}

    def setupResults(self, target_freqs):
        for key in self.results:
            if str(target_freqs) not in self.results[key]:
                self.results[key][str(target_freqs)] = \
                    {i: {freq2: 0 for freq2 in target_freqs} for i in range(len(target_freqs))}

    def printResults(self):
        for method in self.results:
            print method
            for freqs in self.results[method]:
                print freqs
                for row in sorted(self.results[method][freqs]):
                    print row, self.results[method][freqs][row]

    def mainSendingLoop(self, sequence, target_freqs, no_standby):
        print(sequence)
        message = None
        for target, time in sequence:
            self.connections[c.CONNECTION_PSYCHOPY].sendCurrentTarget(target)
            message = self.startPacketSending(time, no_standby, target_freqs, target)
            if message is not None:
                break
        return message

    def sendStartMessages(self):
        for key in self.connections:
            self.connections[key].sendStartMessage()

    def sendStopMessages(self):
        for key in self.connections:
            self.connections[key].sendStopMessage()

    def addProcesses(self, options):
        for key in self.connections:
            self.connections[key].addProcesses(self.getProcessCount(key, options))

    def getProcessCount(self, key, options):
        if key in self.connection_options_key:
            return len(options[self.connection_options_key[key]])
        else:
            return 1

    def sendOptions(self, options):
        for key in self.connections:
            self.connections[key].sendOptions(options)

    def start(self):
        options = self.main_connection.receiveMessageBlock()
        print(options)
        self.addProcesses(options)
        self.sendStartMessages()
        self.sendOptions(options)
        self.setupResults(options[c.DATA_FREQS])
        message = self.mainSendingLoop(
            self.getSequence(options[c.DATA_TEST]),
            options[c.DATA_FREQS],
            not options[c.DATA_TEST][c.TEST_STANDBY]
        )
        self.sendStopMessages()
        self.printResults()
        return message

    def handleEmotivMessages(self, no_standby):
        message = self.connections[c.CONNECTION_EMOTIV].receiveMessagePoll(0.007)
        if message is not None:
            # self.connections[c.CONNECTION_EXTRACTION].sendMessage(message)
            self.connections[c.CONNECTION_PLOT].sendMessage(message)
            if not self.standby or no_standby:
                return 1
        return 0

    def startPacketSending(self, length, no_standby, target_freqs, current_target):
        count = 0
        self.standby = True
        self.standby_freq = target_freqs[-1]
        while count < length:
            main_message = self.main_connection.receiveMessageInstant()
            if main_message is not None:
                return main_message
            count += self.handleEmotivMessages(no_standby)
            # self.connections[c.CONNECTION_PLOT].getMessageInstant()
            self.handleFreqMessages(
                self.connections[c.CONNECTION_EXTRACTION].receiveMessageInstant(),
                no_standby,
                target_freqs,
                current_target
            )
        # Wait for the last result
        self.handleFreqMessages(
            self.connections[c.CONNECTION_EXTRACTION].receiveMessageBlock(),
            no_standby,
            target_freqs,
            current_target
        )
