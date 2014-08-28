__author__ = 'Anti'

import multiprocessing.reduction
import random


class PostOffice(object):
    def __init__(self, main_connection):
        self.main_connection = main_connection
        self.emotiv_connection = []
        self.psychopy_connection = []
        self.plot_connection = []
        self.extraction_connection = []
        self.game_connection = []
        self.results = {"CCA": {}, "PSDA": {}, "CCAPSDA": {}}
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
            if self.main_connection.poll(0.1):
                message = self.main_connection.recv()
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
                elif message == "Start":
                    self.start(self.normalSequence, False)
                elif message == "Start2":
                    self.start(self.normalSequence, True)
                elif message == "Test":
                    self.start(self.randomTestSequence, True)
                elif message == "Threshold":
                    self.calculateThreshold()
                elif message == "Exit":
                    self.sendMessage(self.emotiv_connection, "Exit")
                    self.sendMessage(self.psychopy_connection, "Exit")
                    self.sendMessage(self.plot_connection, "Exit")
                    self.sendMessage(self.extraction_connection, "Exit")
                    self.sendMessage(self.game_connection, "Exit")
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
                else:
                    print "Unknown message:", message

    def calculateThreshold(self):
        self.target_freqs = self.main_connection.recv()
        self.sendMessage(self.extraction_connection, "Start")
        self.sendMessage(self.extraction_connection, self.target_freqs)
        for signal in self.recorded_signals:
            if signal is not None:
                for packet in signal:
                    self.sendMessage(self.extraction_connection, packet)
        self.sendMessage(self.extraction_connection, "Stop")

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

    def getMessages(self, connections, name):
        ret = []
        for i in range(len(connections)-1, -1, -1):
            if connections[i].poll():
                message = connections[i].recv()
                if message == "Close":
                    print name, "pipe closed"
                    connections[i].close()
                    del connections[i]
                else:  # elif name == "Extraction" and isinstance(message, float):
                    ret.append((message, connections[i].recv()))
        return ret

    def handleFreqMessages(self, messages, test=False):
        for freq, class_name in messages:
            self.results[class_name][str(self.target_freqs)][self.current_target][freq] += 1
            if freq == self.standby_freq:
                self.sendMessage(self.psychopy_connection, self.standby and not test)
                self.standby = not self.standby
            if not self.standby or test:
                self.sendMessage(self.psychopy_connection, freq)
                self.sendMessage(self.game_connection, freq)

    def sendMessage(self, connections, message):
        for i in range(len(connections)-1, -1, -1):
            connections[i].send(message)

    def randomTestSequence(self, length, min_length=128*2, max_length=128*4):
        if self.current_target == -1:
            data = []
            asd = {i: length for i in range(len(self.target_freqs))}
            while True:
                target = random.choice(asd.keys())
                time = random.randint(min_length, max_length)
                if asd[target] - time < min_length:
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
        else:
            return [[self.current_target, length]]

    def normalSequence(self, length):
        return [[self.current_target, length]]

    def start(self, function, test):
        length = self.main_connection.recv()
        self.current_target = self.main_connection.recv()-1
        background_data = self.main_connection.recv()
        targets_data = self.main_connection.recv()
        self.target_freqs = self.main_connection.recv()
        self.sendMessage(self.psychopy_connection, "Start")
        self.sendMessage(self.plot_connection, "Start")
        self.sendMessage(self.extraction_connection, "Start")
        self.sendMessage(self.game_connection, "Start")
        self.sendMessage(self.psychopy_connection, background_data)
        self.sendMessage(self.psychopy_connection, targets_data)
        self.sendMessage(self.extraction_connection, self.target_freqs)
        self.sendMessage(self.game_connection, self.target_freqs)
        for key in self.results:
            if str(self.target_freqs) not in self.results[key]:
                self.results[key][str(self.target_freqs)] = {i: {freq2: 0 for freq2 in self.target_freqs} for i in range(-1, len(self.target_freqs))}
            else:
                break
        self.sendMessage(self.emotiv_connection, "Start")
        sequence = function(length)
        print sequence
        for target, time in sequence:
            self.current_target = target
            if target != -1:
                self.sendMessage(self.psychopy_connection, target)
            message = self.startPacketSending(time, test)
            if message is not None:
                break
        self.sendMessage(self.emotiv_connection, "Stop")
        self.sendMessage(self.psychopy_connection, "Stop")
        self.sendMessage(self.plot_connection, "Stop")
        self.sendMessage(self.extraction_connection, "Stop")
        self.sendMessage(self.game_connection, "Stop")
        for method in self.results:
            print method
            for freqs in self.results[method]:
                print freqs
                for row in sorted(self.results[method][freqs]):
                    print row, self.results[method][freqs][row]
        return message

    def startPacketSending(self, length, test):
        count = 0
        self.standby = True
        self.standby_freq = self.target_freqs[-1]
        if test:
            self.sendMessage(self.psychopy_connection, False)
        while count < length:
            if self.main_connection.poll():
                message = self.main_connection.recv()
                return message
            if self.emotiv_connection[0].poll():
                message = self.emotiv_connection[0].recv()
                self.sendMessage(self.extraction_connection, message)
                self.sendMessage(self.plot_connection, message)
                if not self.standby or test:
                    count += 1
            self.getMessages(self.plot_connection, "Plot")
            freqs = self.getMessages(self.extraction_connection, "Extraction")
            self.handleFreqMessages(freqs, test)