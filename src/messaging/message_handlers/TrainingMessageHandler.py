from training import ModelTrainer
from messaging.message_handlers import AbstractMessageHandler
import constants as c


class TrainingMessageHandler(AbstractMessageHandler.MessageHandler):
    def __init__(self, main_connection):
        AbstractMessageHandler.MessageHandler.__init__(self, c.TRAINING_MESSAGES)
        self.main_connection = main_connection
        self.trainer = ModelTrainer.ModelTrainer()

    def handle(self, message):
        if message == c.SEND_RECORDED_FEATURES_MESSAGE:
            self.trainer.setRecordings(self.main_connection.receiveMessageBlock())
        elif message == c.SEND_CLASSIFICATION_OPTIONS:
            self.trainer.setup(self.main_connection.receiveMessageBlock())
        elif message == c.TRAINING_START_MESSAGE:
            self.handleTrainingStart()
        elif message == c.GET_MODEL_MESSAGE:
            self.main_connection.sendMessage(self.trainer.getModel())

    def handleTrainingStart(self):
        self.trainer.start()
        self.main_connection.sendMessage(c.TRAINING_STOPPED_MESSAGE)
