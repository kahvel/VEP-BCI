import Queue
from connections import Connections
from connections.process import ConnectionProcessEnd
import threading


class QueueConnection(Queue.Queue):
    def __init__(self):
        Queue.Queue.__init__(self)

    def send(self, message):
        self.put(message)

    def recv(self):
        return self.get()

    def poll(self, dummy=None):
        return True

    def close(self):
        pass


class ProcessQueueConnection(ConnectionProcessEnd.Connection):
    def __init__(self, connection, receiving_queue):
        ConnectionProcessEnd.Connection.__init__(self, connection, "ProcessQueueConnectionName")
        self.receiving_queue = receiving_queue

    def receiveMessage(self):
        return self.receiving_queue.recv()

    def receiveOptions(self):
        return self.receiveMessage()


class PostOfficeQueueConnection(Connections.Connection):
    def __init__(self, process):
        Connections.Connection.__init__(self, process, ProcessQueueConnection)
        self.connection = None
        self.receiving_queue = QueueConnection()

    def receiveMessage(self):
        return self.receiving_queue.recv()

    def newProcess(self):
        self.connection = QueueConnection()
        threading.Thread(target=self.process, args=(self.connection_other_end(self.receiving_queue, self.connection),)).start()
        return self.connection

    # def setupSuccessful(self):
    #     return True

    def receiveExtractionMessages(self):
        return self.receiveMessage()
