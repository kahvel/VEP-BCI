from messaging.message_handlers import AbstractMessageHandler
import constants as c


class MainWindowMessageHandler(AbstractMessageHandler.MessageHandler):
    def __init__(self, main_frame, buttons_state_controller, input_parser, connection):
        AbstractMessageHandler.MessageHandler.__init__(self, c.MAIN_WINDOW_MESSAGES)
        self.main_frame = main_frame
        self.buttons_state_controller = buttons_state_controller
        self.options = None
        self.input_parser = input_parser
        self.connection = connection
        self.stopped = True

    def handle(self, message):
        if message == c.BCI_STOPPED_MESSAGE:
            self.handleBciStopped()
        elif message == c.SETUP_SUCCEEDED_MESSAGE:
            self.handleSetupSucceeded()
        elif message == c.SETUP_FAILED_MESSAGE:
            self.handleSetupFailed()
        elif message == c.TRAINING_STOPPED_MESSAGE:
            self.handleTrainingStopped()

    def handleBciStopped(self):
        self.buttons_state_controller.stopClicked()
        self.stopped = True
        self.evokeTrialEndedEvent()

    def handleSetupSucceeded(self):
        print "Setup succeeded!"
        self.buttons_state_controller.enableStart()

    def handleSetupFailed(self):
        print "Setup failed!"
        self.buttons_state_controller.disableStart()

    def handleTrainingStopped(self):
        self.evokeTrainingEndedEvent()

    def setup(self):
        not_validated = self.main_frame.getNotValidated()
        if len(not_validated) != 0:
            print(not_validated)
        else:
            self.options = self.input_parser.parseData(self.main_frame.getValue()[c.MAIN_NOTEBOOK])
            self.connection.sendMessage(c.SETUP_MESSAGE)
            self.connection.sendMessage(self.options)

    def start(self):
        if self.options != self.input_parser.parseData(self.main_frame.getValue()[c.MAIN_NOTEBOOK]):
            print("Warning: options were changed, but setup was not clicked")
        self.connection.sendMessage(c.START_MESSAGE)
        self.buttons_state_controller.startClicked()
        self.stopped = False

    def stop(self):
        self.connection.sendMessage(c.STOP_MESSAGE)

    def isStopped(self):
        return self.stopped

    def evokeTrialEndedEvent(self):
        self.main_frame.sendEventToRoot(lambda x: x.trialEndedEvent())

    def evokeTrainingEndedEvent(self):
        self.main_frame.sendEventToRoot(lambda x: x.trainingEndedEvent())
