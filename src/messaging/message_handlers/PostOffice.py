from connections.postoffice import MasterConnection, ConnectionPostOfficeEnd
from messaging.message_handlers import AbstractMessageHandler, BciMessageHandler
import messaging.message_handlers.TrainingMessageHandler

import constants as c


class PostOffice(AbstractMessageHandler.MessageHandler):
    def __init__(self):
        AbstractMessageHandler.MessageHandler.__init__(self, c.POST_OFFICE_MESSAGES)
        self.main_connection = ConnectionPostOfficeEnd.MainConnection()
        self.connections = MasterConnection.MasterConnection()
        self.bci_message_handler = BciMessageHandler.BciMessageHandler(self.main_connection, self.connections)
        self.training_message_handler = messaging.message_handlers.TrainingMessageHandler.TrainingMessageHandler(self.main_connection)
        self.exit_flag = False
        self.waitMessages()

    def waitMessages(self):
        while not self.exit_flag:
            self.handle(self.main_connection.receiveMessagePoll(0.1))
            self.handleNonMessages()
        self.connections.close()
        self.main_connection.close()

    def handleNonMessages(self):
        if self.bci_message_handler.control_message_handler.threadJustDied():
            self.bci_message_handler.handleThreadDied()

    def handle(self, message):
        if message is not None:
            if self.bci_message_handler.canHandle(message):
                self.bci_message_handler.handle(message)
            elif self.training_message_handler.canHandle(message):
                self.training_message_handler.handle(message)
            elif message in c.ROBOT_MESSAGES:
                self.connections.sendRobotMessage(message)
            elif message == c.EXIT_MESSAGE:
                self.setExitFlag(True)
            else:
                print("Unknown message in PostOffice: " + str(message))

    def setExitFlag(self, value):
        self.exit_flag = value
