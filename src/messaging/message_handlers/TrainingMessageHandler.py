from training import ModelTrainer
from messaging.message_handlers import AbstractMessageHandler
import constants as c


class TrainingGetDataHandler(AbstractMessageHandler.MessageHandler):
    def __init__(self, main_connection, trainer):
        AbstractMessageHandler.MessageHandler.__init__(self, c.TRAINING_GET_DATA_MESSAGES)
        self.main_connection = main_connection
        self.trainer = trainer

    def handle(self, message):
        if message == c.GET_TRAINING_DATA_MESSAGE:
            self.main_connection.sendMessage(self.trainer.getTrainingData())
        elif message == c.GET_TRAINING_LABELS_MESSAGE:
            self.main_connection.sendMessage(self.trainer.getTrainingLabels())
        elif message == c.GET_VALIDATION_DATA_MESSAGE:
            self.main_connection.sendMessage(self.trainer.getValidationData())
        elif message == c.GET_VALIDATION_LABELS_MESSAGE:
            self.main_connection.sendMessage(self.trainer.getValidationLabels())
        elif message == c.GET_MODEL_MESSAGE:
            self.main_connection.sendMessage(self.trainer.getModel())
        elif message == c.GET_SECOND_MODEL_MESSAGE:
            self.main_connection.sendMessage(self.trainer.getSecondModel())
        elif message == c.GET_MIN_MAX_MESSAGE:
            self.main_connection.sendMessage(self.trainer.getMinMax())
        elif message == c.GET_THRESHOLDS_MESSAGE:
            self.main_connection.sendMessage(self.trainer.getThresholds())
        elif message == c.GET_TRAINING_ROC_MESSAGE:
            self.main_connection.sendMessage(self.trainer.getTrainingRoc())
        elif message == c.GET_VALIDATION_ROC_MESSAGE:
            self.main_connection.sendMessage(self.trainer.getValidationRoc())
        elif message == c.GET_USED_FEATURES_MESSAGE:
            self.main_connection.sendMessage(self.trainer.getUsedFeatures())


class TrainingSendDataHandler(AbstractMessageHandler.MessageHandler):
    def __init__(self, main_connection, trainer):
        AbstractMessageHandler.MessageHandler.__init__(self, c.TRAINING_SEND_DATA_MESSAGES)
        self.main_connection = main_connection
        self.trainer = trainer

    def handle(self, message):
        if message == c.SEND_RECORDED_FEATURES_MESSAGE:
            self.trainer.setRecordings(self.main_connection.receiveMessageBlock())
        elif message == c.SEND_CLASSIFICATION_OPTIONS:
            self.trainer.setup(self.main_connection.receiveMessageBlock())


class TrainingDataExchngeHandler(AbstractMessageHandler.MessageHandler):
    def __init__(self, main_connection, trainer):
        AbstractMessageHandler.MessageHandler.__init__(self, c.TRAINING_DATA_EXCHANGE_MESSAGES)
        self.get_data_handler = TrainingGetDataHandler(main_connection, trainer)
        self.send_data_handler = TrainingSendDataHandler(main_connection, trainer)

    def handle(self, message):
        if self.get_data_handler.canHandle(message):
            self.get_data_handler.handle(message)
        elif self.send_data_handler.canHandle(message):
            self.send_data_handler.handle(message)


class TrainingControlsHandler(AbstractMessageHandler.MessageHandler):
    def __init__(self, main_connection, trainer):
        AbstractMessageHandler.MessageHandler.__init__(self, c.TRAINING_CONTROL_MESSAGES)
        self.main_connection = main_connection
        self.trainer = trainer

    def handle(self, message):
        if message == c.TRAINING_START_MESSAGE:
            self.handleTrainingStart()

    def handleTrainingStart(self):
        self.trainer.start()
        self.main_connection.sendMessage(c.TRAINING_STOPPED_MESSAGE)


class TrainingMessageHandler(AbstractMessageHandler.MessageHandler):
    def __init__(self, main_connection):
        AbstractMessageHandler.MessageHandler.__init__(self, c.TRAINING_MESSAGES)
        self.trainer = ModelTrainer.ModelTrainer()
        self.training_control_handler = TrainingControlsHandler(main_connection, self.trainer)
        self.data_exchange_handler = TrainingDataExchngeHandler(main_connection, self.trainer)

    def handle(self, message):
        if self.training_control_handler.canHandle(message):
            self.training_control_handler.handle(message)
        elif self.data_exchange_handler.canHandle(message):
            self.data_exchange_handler.handle(message)
