import constants as c


class PostOfficeMessageHandler(object):
    def __init__(self, main_window, buttons_state_controller, input_parser):
        self.main_window = main_window
        self.buttons_state_controller = buttons_state_controller
        self.options = None
        self.input_parser = input_parser
        self.connection = main_window.connection
        self.stopped = True

    def canHandle(self, message):
        return message in c.BCI_MESSAGES

    def handle(self, message):
        if message == c.STOP_MESSAGE:
            self.stop()
        elif message == c.SUCCESS_MESSAGE:  # Setup was successful
            self.buttons_state_controller.enableStart()
        elif message == c.FAIL_MESSAGE:  # Setup failed
            self.buttons_state_controller.disableStart()

    def setup(self):
        not_validated = self.main_window.main_frame.getNotValidated()
        if len(not_validated) != 0:
            print(not_validated)
        else:
            self.options = self.input_parser.parseData(self.main_window.main_frame.getValue()[c.MAIN_NOTEBOOK])
            self.connection.sendMessage(c.SETUP_MESSAGE)
            self.connection.sendMessage(self.options)

    def start(self):
        if self.options != self.input_parser.parseData(self.main_window.main_frame.getValue()[c.MAIN_NOTEBOOK]):
            print("Warning: options were changed, but setup was not clicked")
        self.connection.sendMessage(c.START_MESSAGE)
        self.buttons_state_controller.startClicked()
        self.stopped = False

    def stop(self):
        self.buttons_state_controller.stopClicked()
        self.connection.sendMessage(c.STOP_MESSAGE)
        self.stopped = True

    def isStopped(self):
        return self.stopped
