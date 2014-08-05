__author__ = 'Anti'
import multiprocessing.reduction


class PostOffice(object):
    def __init__(self, main_connection):
        self.main_connection = main_connection
        self.emotiv_connection = []
        self.psychopy_connection = []
        self.plot_connection = []
        self.extraction_connection = []
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
                elif message == "Start":
                    self.sendMessage(self.emotiv_connection, "Start")
                    self.sendMessage(self.psychopy_connection, "Start")
                    self.sendMessage(self.plot_connection, "Start")
                    self.sendMessage(self.extraction_connection, "Start")
                    self.sendMessage(self.psychopy_connection, self.main_connection.recv())
                    self.sendMessage(self.extraction_connection, self.main_connection.recv())
                    self.sendMessage(self.extraction_connection, self.main_connection.recv())
                    message = self.start()
                    if message == "Stop":
                        self.sendMessage(self.emotiv_connection, "Stop")
                        self.sendMessage(self.psychopy_connection, "Stop")
                        self.sendMessage(self.plot_connection, "Stop")
                        self.sendMessage(self.extraction_connection, "Stop")
                elif message == "Exit":
                    self.sendMessage(self.emotiv_connection, "Exit")
                    self.sendMessage(self.psychopy_connection, "Exit")
                    self.sendMessage(self.plot_connection, "Exit")
                    self.sendMessage(self.extraction_connection, "Exit")
                    return
                elif message == "Record neutral":
                    self.sendMessage(self.emotiv_connection, "Start")
                    self.recordSignal(self.main_connection.recv())
                    self.sendMessage(self.emotiv_connection, "Stop")
                elif message == "Record target":
                    self.sendMessage(self.psychopy_connection, "Start")
                    self.sendMessage(self.psychopy_connection, self.main_connection.recv())
                    self.sendMessage(self.emotiv_connection, "Start")
                    self.recordSignal(self.main_connection.recv())
                    self.sendMessage(self.emotiv_connection, "Stop")
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
                    self.sendMessage(self.psychopy_connection, message)

    def sendMessage(self, connections, message):
        for i in range(len(connections)-1, -1, -1):
            connections[i].send(message)

    def start(self):
        while True:
            if self.main_connection.poll():
                message = self.main_connection.recv()
                return message
            if self.emotiv_connection[0].poll():
                message = self.emotiv_connection[0].recv()
                self.sendMessage(self.extraction_connection, message)
                self.sendMessage(self.plot_connection, message)
            self.handleMessage(self.plot_connection, "Plot")
            self.handleMessage(self.extraction_connection, "Extraction")

    def exit(self):
        pass