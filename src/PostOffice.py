import constants as c
from connections.postoffice import MasterConnection, ConnectionPostOfficeEnd
import BCI
import Training
import Recording


class PostOffice(object):
    def __init__(self):
        self.main_connection = ConnectionPostOfficeEnd.MainConnection()
        self.connections = MasterConnection.MasterConnection()
        self.recording = Recording.Recording()
        self.bci = BCI.BCI(self.connections, self.main_connection, self.recording)
        self.training = Training.Training(self.connections, self.main_connection, self.recording)
        self.options = None
        self.message_counter = None
        self.waitConnections()

    def waitConnections(self):
        message = None
        while True:
            if message is not None:
                if message == c.START_MESSAGE:
                    message = self.bci.start(self.options)
                    continue
                elif message == c.SETUP_MESSAGE:
                    self.options = self.main_connection.receiveMessageBlock()
                    setup_message = self.bci.setup(self.options)
                    if setup_message == c.FAIL_MESSAGE:
                        self.connections.close()
                    print("Setup " + setup_message + "!")
                    self.main_connection.sendMessage(setup_message)
                elif message == c.STOP_MESSAGE:
                    print("Stop PostOffice")
                elif message == c.RESET_RESULTS_MESSAGE:
                    self.bci.resetResults()
                elif message == c.SHOW_RESULTS_MESSAGE:
                    print(self.bci.getResults())
                elif message == c.SAVE_RESULTS_MESSAGE:
                    self.main_connection.sendMessage(self.bci.getResults())
                elif message == c.LOAD_EEG_MESSAGE:
                    file_content = self.main_connection.receiveMessageBlock()
                    self.bci.loadEeg(file_content)
                elif message == c.SAVE_EEG_MESSAGE:
                    self.main_connection.sendMessage(self.bci.saveEeg())
                elif message == c.RESET_EEG_MESSAGE:
                    self.bci.resetRecording()
                elif message == c.EXIT_MESSAGE:
                    self.exit()
                    return
                elif message in c.ROBOT_COMMANDS:
                    self.connections.sendRobotMessage(message)
                elif message == c.TRAIN_WITH_CURRENT_OPTIONS_MESSAGE:
                    options = self.main_connection.receiveMessageBlock()
                    self.training.setupPackets()
                    self.training.setup(options)
                    self.training.start(options)
                else:
                    print("Unknown message in PostOffice: " + str(message))
            message = self.main_connection.receiveMessagePoll(0.1)

    def exit(self):
        self.connections.close()
        self.main_connection.close()
