import constants as c


class PostOffice(object):
    def __init__(self, main_connection, connections, bci_controller):
        self.main_connection = main_connection
        self.connections = connections
        self.bci_controller = bci_controller
        self.bci_message_handler = StartStopSetupHandler(self.bci_controller, self.main_connection, self.connections, self.setExitFlag)
        self.exit_flag = False
        self.waitConnections()

    def waitConnections(self):
        while not self.exit_flag:
            message = self.main_connection.receiveMessagePoll(0.1)
            if message is not None:
                if self.bci_message_handler.canHandle(message):
                    self.bci_message_handler.handle(message)
                elif message == c.RESET_RESULTS_MESSAGE:
                    self.bci_controller.resetResults()
                elif message == c.SHOW_RESULTS_MESSAGE:
                    print(self.bci_controller.getResults())
                elif message == c.SAVE_RESULTS_MESSAGE:
                    self.main_connection.sendMessage(self.bci_controller.getResults())
                elif message == c.LOAD_EEG_MESSAGE:
                    file_content = self.main_connection.receiveMessageBlock()
                    self.bci_controller.loadEeg(file_content)
                elif message == c.SAVE_EEG_MESSAGE:
                    self.main_connection.sendMessage(self.bci_controller.saveEeg())
                elif message == c.RESET_EEG_MESSAGE:
                    self.bci_controller.resetRecording()
                elif message in c.ROBOT_COMMANDS:
                    self.connections.sendRobotMessage(message)
                else:
                    print("Unknown message in PostOffice: " + str(message))
        self.connections.close()
        self.main_connection.close()

    def setExitFlag(self, value):
        self.exit_flag = value


class StartStopSetupHandler(object):
    def __init__(self, controller, main_connection, connections, setExitFlag):
        self.controller = controller
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
        message = self.controller.start(self.options)
        if message is not None:
            self.handle(message)

    def handleSetup(self):
        self.options = self.main_connection.receiveMessageBlock()
        setup_message = self.controller.setup(self.options)
        if setup_message == c.FAIL_MESSAGE:
            self.connections.close()
        print("Setup " + setup_message + "!")
        self.main_connection.sendMessage(setup_message)

    def canHandle(self, message):
        return message in c.BCI_MESSAGES
