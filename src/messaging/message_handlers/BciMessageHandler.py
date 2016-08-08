from messaging.message_handlers import AbstractMessageHandler
import BCI
import constants as c


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
        self.options = None
        self.main_connection = main_connection
        self.connections = connections

    def handle(self, message):
        if message == c.START_MESSAGE:
            self.handleStart()
        elif message == c.SETUP_MESSAGE:
            self.handleSetup()
        elif message == c.STOP_MESSAGE:
            print("Stop PostOffice")

    def handleStart(self):
        message = self.bci_controller.start(self.options)
        if message is not None:
            self.handle(message)

    def handleSetup(self):
        self.options = self.main_connection.receiveMessageBlock()
        setup_message = self.bci_controller.setup(self.options)
        if setup_message == c.SETUP_FAILED_MESSAGE:
            self.connections.close()
        print("Setup " + setup_message + "!")
        self.main_connection.sendMessage(setup_message)


class BciMessageHandler(AbstractMessageHandler.MessageHandler):
    def __init__(self, main_connection, connections):
        AbstractMessageHandler.MessageHandler.__init__(self, c.BCI_MESSAGES)
        bci_controller = BCI.BCI(connections, main_connection)
        self.control_message_handler = BciControlsHandler(bci_controller, main_connection, connections)
        self.data_exchange_handler = BciDataExchangeHandler(main_connection, bci_controller)

    def handle(self, message):
        if self.control_message_handler.canHandle(message):
            self.control_message_handler.handle(message)
        elif self.data_exchange_handler.canHandle(message):
            self.data_exchange_handler.handle(message)
