from messaging.message_handlers import AbstractMessageHandler
import BCI
import constants as c

import threading


class BciDataExchangeHandler(AbstractMessageHandler.MessageHandler):
    def __init__(self, main_connection, bci_controller):
        """
        Handles messages coming from main window to post office.
        Sends requested data back to main window.
        :param main_connection:
        :param bci_controller:
        :return:
        """
        AbstractMessageHandler.MessageHandler.__init__(self, c.BCI_DATA_EXCHANGE_MESSAGES)
        self.main_connection = main_connection
        self.bci_controller = bci_controller

    def handle(self, message):
        if message == c.GET_RECORDED_EEG_MESSAGE:
            self.main_connection.sendMessage(self.bci_controller.getRecordedEeg())
        elif message == c.GET_RECORDED_FEATURES_MESSAGE:
            self.main_connection.sendMessage(self.bci_controller.getRecordedFeatures())
        elif message == c.GET_RECORDED_FREQUENCIES_MESSAGE:
            self.main_connection.sendMessage(self.bci_controller.getRecordedFrequencies())
        elif message == c.GET_RESULTS_MESSAGE:
            self.main_connection.sendMessage(self.bci_controller.getResults())
        elif message == c.GET_NEW_RESULTS_MESSAGE:
            self.main_connection.sendMessage(self.bci_controller.getNewResults())


class BciControlsHandler(AbstractMessageHandler.MessageHandler):
    def __init__(self, bci_controller, main_connection, connections):
        """
        Handles messages coming from main window to post office. Either starts, sets up or stops the BCI.
        Also sends message to main window about whether setup succeeded or failed.
        :param bci_controller:
        :param main_connection:
        :param connections:
        :return:
        """
        AbstractMessageHandler.MessageHandler.__init__(self, c.BCI_CONTROL_MESSAGES)
        self.bci_controller = bci_controller
        self.main_connection = main_connection
        self.connections = connections
        self.bci_thread = None

    def handle(self, message):
        if message == c.START_MESSAGE:
            self.handleStart()
        elif message == c.SETUP_MESSAGE:
            self.handleSetup()
        elif message == c.STOP_MESSAGE:
            self.handleStop()

    def handleStop(self):
        self.bci_controller.setExitFlag(True)

    def handleStart(self):
        self.bci_thread = threading.Thread(target=self.bci_controller.start)
        self.bci_thread.start()

    def handleSetup(self):
        options = self.main_connection.receiveMessageBlock()
        self.connections.setup(options)
        self.bci_controller.setup(options)
        if self.connections.setupSuccessful() and self.bci_controller.setupSucceeded():
            self.main_connection.sendMessage(c.SETUP_SUCCEEDED_MESSAGE)
        else:
            self.main_connection.sendMessage(c.SETUP_FAILED_MESSAGE)
            self.connections.close()

    def checkThread(self):
        if not self.bci_thread.isAlive():
            self.bci_thread = None
            return True
        else:
            return False

    def threadJustDied(self):
        if self.bci_thread is not None:
            return self.checkThread()
        else:
            return False


class BciMessageHandler(AbstractMessageHandler.MessageHandler):
    def __init__(self, main_connection, connections):
        AbstractMessageHandler.MessageHandler.__init__(self, c.BCI_MESSAGES)
        self.main_connection = main_connection
        bci_controller = BCI.BCI(connections)
        self.control_message_handler = BciControlsHandler(bci_controller, main_connection, connections)
        self.data_exchange_handler = BciDataExchangeHandler(main_connection, bci_controller)

    def handle(self, message):
        if self.control_message_handler.canHandle(message):
            self.control_message_handler.handle(message)
        elif self.data_exchange_handler.canHandle(message):
            self.data_exchange_handler.handle(message)

    def handleThread(self):
        if self.control_message_handler.threadJustDied():
            self.handleThreadDied()

    def handleThreadDied(self):
        self.main_connection.sendMessage(c.BCI_STOPPED_MESSAGE)
