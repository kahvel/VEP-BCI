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
                    self.start(self.normalSequence)
                elif message == "Test":
                    self.start(self.randomTestSequence)
                elif message == "Exit":
                    self.sendMessage(self.emotiv_connection, "Exit")
                    self.sendMessage(self.psychopy_connection, "Exit")
                    self.sendMessage(self.plot_connection, "Exit")
                    self.sendMessage(self.extraction_connection, "Exit")
                    self.sendMessage(self.game_connection, "Exit")
                    while True:  # wait until all connections are closed
                        self.handleMessage(self.psychopy_connection, "Psychopy")
                        self.handleMessage(self.plot_connection, "Plot")
                        self.handleMessage(self.extraction_connection, "Extraction")
                        self.handleMessage(self.game_connection, "Game")
                        if len(self.psychopy_connection)+len(self.plot_connection)+len(self.extraction_connection) == 0:
                            return
                elif message == "Record neutral":
                    self.sendMessage(self.emotiv_connection, "Start")
                    self.recordSignal(self.main_connection.recv())
                    self.sendMessage(self.emotiv_connection, "Stop")
                elif message == "Record target":
                    self.sendMessage(self.psychopy_connection, "Start")
                    self.sendMessage(self.psychopy_connection, self.main_connection.recv())
                    self.sendMessage(self.psychopy_connection, self.main_connection.recv())
                    self.sendMessage(self.emotiv_connection, "Start")
                    self.recordSignal(self.main_connection.recv())
                    self.sendMessage(self.emotiv_connection, "Stop")
                    self.sendMessage(self.psychopy_connection, "Stop")
                else:
                    print "Unknown message:", message

    def recordSignal(self, length):
        signal = []
        while len(signal) < length:
            if self.main_connection.poll():
                message = self.main_connection.recv()
                return message
            if self.emotiv_connection[0].poll():
                message = self.emotiv_connection[0].recv()
                signal.append(message)
        self.main_connection.send(signal)

    def handleMessage(self, connections, name):
        for i in range(len(connections)-1, -1, -1):
            if connections[i].poll():
                message = connections[i].recv()
                if message == "Close":
                    print name, "pipe closed"
                    connections[i].close()
                    del connections[i]
                elif name == "Extraction" and isinstance(message, float):
                    class_name = connections[i].recv()
                    self.results[class_name][str(self.target_freqs)][self.current_target][message] += 1
                    self.sendMessage(self.psychopy_connection, message)
                    self.sendMessage(self.game_connection, message)

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
                print target, time, asd
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

    def start(self, function):
        length = self.main_connection.recv()
        self.current_target = self.main_connection.recv()-1
        background_data = self.main_connection.recv()
        targets_data = self.main_connection.recv()
        self.target_freqs = self.main_connection.recv()
        recorded_signals = self.main_connection.recv()
        self.sendMessage(self.psychopy_connection, "Start")
        self.sendMessage(self.plot_connection, "Start")
        self.sendMessage(self.extraction_connection, "Start")
        self.sendMessage(self.game_connection, "Start")
        self.sendMessage(self.psychopy_connection, background_data)
        self.sendMessage(self.psychopy_connection, targets_data)
        self.sendMessage(self.extraction_connection, self.target_freqs)
        self.sendMessage(self.game_connection, self.target_freqs)
        self.sendMessage(self.extraction_connection, recorded_signals)
        for key in self.results:
            if str(self.target_freqs) not in self.results[key]:
                self.results[key][str(self.target_freqs)] = {i: {freq2: 0 for freq2 in self.target_freqs} for i in range(-1, len(self.target_freqs))}
            else:
                break
        self.sendMessage(self.emotiv_connection, "Start")
        random_sequence = function(length)
        print random_sequence
        for target, time in random_sequence:
            self.current_target = target
            if target != -1:
                self.sendMessage(self.psychopy_connection, target)
            message = self.startPacketSending(time)
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

    def startPacketSending(self, length):
        count = 0
        while count < length:
            if self.main_connection.poll():
                message = self.main_connection.recv()
                return message
            if self.emotiv_connection[0].poll():
                count += 1
                message = self.emotiv_connection[0].recv()
                self.sendMessage(self.extraction_connection, message)
                self.sendMessage(self.plot_connection, message)
            self.handleMessage(self.plot_connection, "Plot")
            self.handleMessage(self.extraction_connection, "Extraction")