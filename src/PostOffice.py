from training import ModelTrainer
import constants as c


class PostOffice(object):
    def __init__(self, main_connection, connections, bci_controller):
        self.main_connection = main_connection
        self.connections = connections
        self.bci_controller = bci_controller
        self.trainer = ModelTrainer.ModelTrainer()
        self.bci_message_handler = StartStopSetupHandler(self.bci_controller, self.main_connection, self.connections, self.setExitFlag)
        self.exit_flag = False
        self.waitConnections()

    def waitConnections(self):
        while not self.exit_flag:
            message = self.main_connection.receiveMessagePoll(0.1)
            if message is not None:
                if self.bci_message_handler.canHandle(message):
                    self.bci_message_handler.handle(message)
                elif message == c.GET_RECORDED_EEG:
                    self.main_connection.sendMessage(self.bci_controller.getRecordedEeg())
                elif message == c.GET_RECORDED_FEATURES:
                    self.main_connection.sendMessage(self.bci_controller.getRecordedFeatures())
                elif message == c.GET_RECORDED_FREQUENCIES:
                    self.main_connection.sendMessage(self.bci_controller.getRecordedFrequencies())
                elif message == c.GET_RESULTS_MESSAGE:
                    self.main_connection.sendMessage(self.bci_controller.getResults())
                elif message == c.GET_NEW_RESULTS_MESSAGE:
                    self.main_connection.sendMessage(self.bci_controller.getNewResults())
                elif message == c.SEND_RECORDED_FEATURES:
                    self.trainer.setRecordings(self.main_connection.receiveMessageBlock())
                elif message == c.SEND_CLASSIFICATION_OPTIONS:
                    self.trainer.setup(self.main_connection.receiveMessageBlock())
                elif message == c.TRAINING_START_MESSAGE:
                    self.trainer.start()
                elif message in c.ROBOT_COMMANDS:
                    self.connections.sendRobotMessage(message)
                else:
                    print("Unknown message in PostOffice: " + str(message))
        self.connections.close()
        self.main_connection.close()

    def setExitFlag(self, value):
        self.exit_flag = value


class StartStopSetupHandler(object):
    def __init__(self, bci_controller, main_connection, connections, setExitFlag):
        self.bci_controller = bci_controller
        self.options = None
        self.main_connection = main_connection
        self.connections = connections
        self.setExitFlag = setExitFlag

    def handle(self, message):
        if message == c.START_MESSAGE:
            self.handleStart()
        elif message == c.SETUP_MESSAGE:
            self.handleSetup()
        elif message == c.STOP_MESSAGE:
            print("Stop PostOffice")
        elif message == c.EXIT_MESSAGE:
            self.setExitFlag(True)

    def handleStart(self):
        message = self.bci_controller.start(self.options)
        if message is not None:
            self.handle(message)

    def handleSetup(self):
        self.options = self.main_connection.receiveMessageBlock()
        setup_message = self.bci_controller.setup(self.options)
        if setup_message == c.FAIL_MESSAGE:
            self.connections.close()
        print("Setup " + setup_message + "!")
        self.main_connection.sendMessage(setup_message)

    def canHandle(self, message):
        return message in c.BCI_MESSAGES
