__author__ = 'Anti'

import multiprocessing.reduction
import random
import numpy as np
import constants as c
import Main


class PostOffice(object):
    def __init__(self):
        self.main_connection = SingleConnection(Main.runMainWindow)
        self.emotiv_connection = []
        self.psychopy_connection = []
        self.plot_connection = []
        self.extraction_connection = []
        self.game_connection = []
        self.results = None
        self.resetResults()
        self.target_freqs = None
        self.current_target = None
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
        self.target_freqs = self.main_connection.recv()
        all_results = []
        for signal in self.recorded_signals:
            if signal is not None:
                self.sendMessage(self.extraction_connection, "Start")
                self.sendMessage(self.extraction_connection, self.target_freqs)
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

    def handleFreqMessages(self, messages, no_standby):
        for result in messages:
            for freq, class_name in result:
                self.results[class_name][str(self.target_freqs)][self.current_target][freq] += 1
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

    def randomSequence(self, options):
        data = []
        asd = {i: options["Length"] for i in range(len(self.target_freqs))}
        while True:
            target = random.choice(asd.keys())
            time = random.randint(options["Min"], options["Max"])
            if asd[target] - time < options["Min"]:
                time = asd[target]
            asd[target] = asd[target]-time
            if len(data) > 0 and data[-1][0] == target:
                data[-1][1] += time
            else:
                data.append([target, time])
            if asd[target] == 0:
                del asd[target]
                if asd == {}:
                    break
        return data

    def normalSequence(self, options):
        return [[self.current_target, options["Length"]]]

    def getSequence(self, options):
        if options["Random"]:
            return self.randomSequence(options)
        else:
            return self.normalSequence(options)

    def resetResults(self):
        self.results = {name: {} for name in c.EXTRACTION_METHOD_NAMES}

    def setupResults(self):
        for key in self.results:
            if str(self.target_freqs) not in self.results[key]:
                self.results[key][str(self.target_freqs)] = \
                    {i: {freq2: 0 for freq2 in self.target_freqs} for i in range(len(self.target_freqs))}

    def printResults(self):
        for method in self.results:
            print method
            for freqs in self.results[method]:
                print freqs
                for row in sorted(self.results[method][freqs]):
                    print row, self.results[method][freqs][row]

    def sendCurrentTarget(self, target):
        if target != -1:
            self.sendMessage(self.psychopy_connection, target)

    def mainSendingLoop(self, options):
        sequence = self.getSequence(options)
        no_standby = not options["Standby"]
        print sequence
        for target, time in sequence:
            self.current_target = target
            self.sendCurrentTarget(target)
            message = self.startPacketSending(time, no_standby)
            if message is not None:
                break
        return message

    def sendStartMessages(self, background_data, targets_data):
        self.sendMessage(self.psychopy_connection,   c.START_MESSAGE)
        self.sendMessage(self.plot_connection,       c.START_MESSAGE)
        self.sendMessage(self.extraction_connection, c.START_MESSAGE)
        self.sendMessage(self.game_connection,       c.START_MESSAGE)
        self.sendMessage(self.psychopy_connection,   background_data)
        self.sendMessage(self.psychopy_connection,   targets_data)
        self.sendMessage(self.extraction_connection, self.target_freqs)
        self.sendMessage(self.game_connection,       self.target_freqs)
        self.sendMessage(self.emotiv_connection,     c.START_MESSAGE)

    def sendStopMessages(self):
        self.sendMessage(self.emotiv_connection,     c.STOP_MESSAGE)
        self.sendMessage(self.psychopy_connection,   c.STOP_MESSAGE)
        self.sendMessage(self.plot_connection,       c.STOP_MESSAGE)
        self.sendMessage(self.extraction_connection, c.STOP_MESSAGE)
        self.sendMessage(self.game_connection,       c.STOP_MESSAGE)

    # def newProcess(self, func, *args):
    #     new_to_post_office, post_office_to_new = multiprocessing.Pipe()
    #     multiprocessing.Process(target=func, args=(new_to_post_office, args)).start()
    #
    #
    # def setupExtraction(self, options):
    #     for tab in options:


    def start(self):
        options = self.main_connection.receiveMessageBlock()
        print(options)
        self.current_target = options[c.DATA_TEST][c.TEST_TARGET]
        self.target_freqs = options[c.DATA_FREQS]
        # self.setupExtraction(options[c.DATA_EXTRACTION])

        self.sendStartMessages(options[c.DATA_BACKGROUND], options[c.DATA_TARGETS])
        self.setupResults()
        message = self.mainSendingLoop(options)
        self.sendStopMessages()
        self.printResults()
        return message

    def handleEmotivMessages(self, no_standby):
        if self.emotiv_connection[0].poll():
            message = self.emotiv_connection[0].recv()
            self.sendMessage(self.extraction_connection, message)
            self.sendMessage(self.plot_connection, message)
            if not self.standby or no_standby:
                return 1
        return 0

    def sendStandbyMessage(self, no_standby):
        if no_standby:
            self.sendMessage(self.psychopy_connection, False)

    def startPacketSending(self, length, no_standby):
        count = 0
        self.standby = True
        self.standby_freq = self.target_freqs[-1]
        self.sendStandbyMessage(no_standby)
        while count < length:
            main_message = self.main_connection.receiveMessageInstant()
            if main_message is not None:
                return main_message
            count += self.handleEmotivMessages(no_standby)
            self.getMessages(self.plot_connection, "Plot")
            self.handleFreqMessages(self.getMessages(self.extraction_connection, "Extraction"), no_standby)
        # Wait for the last result
        self.handleFreqMessages(self.getMessages(self.extraction_connection, "Extraction", poll=lambda x: x.poll(True)),
                                no_standby)


class AbstractConnection(object):
    def __init__(self, function):
        self.func = function

    def newProcess(self, *args):
        from_process, to_process = multiprocessing.Pipe()
        multiprocessing.Process(target=self.func, args=(from_process,)).start()
        return to_process

    def sendMessage(self, message):
        raise NotImplementedError("sendMessage not implemented!")

    def sendStartMessage(self):
        self.sendMessage(c.START_MESSAGE)

    def sendStopMessage(self):
        self.sendMessage(c.STOP_MESSAGE)


class SingleConnection(AbstractConnection):
    def __init__(self, function, *args):
        AbstractConnection.__init__(self, function)
        self.connection = self.newProcess(args)

    def sendMessage(self, message):
        self.connection.send(message)

    def receiveMessageInstant(self):
        if self.connection.poll():  # If no timeout, returns immediately. If None, timeout is infinite.
            return self.connection.recv()

    def receiveMessagePoll(self, timeout):
        if self.connection.poll(timeout):
            return self.connection.recv()

    def receiveMessageBlock(self):
        if self.connection.poll(None):
            return self.connection.recv()
        else:
            print("Warning! Infinite poll returned False.")


class MultipleConnections(AbstractConnection):
    def __init__(self, function):
        AbstractConnection.__init__(self, function)
        self.connections = []

    def sendMessage(self, message):
        for connection in self.connections:
            connection.send(message)

    def addProcess(self, *args):
        self.connections.append(self.newProcess(args))
