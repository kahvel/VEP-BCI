import random

import constants as c
from connections import MasterConnection, ConnectionPostOfficeEnd
import Results
import Training
import TargetIdentification
import Standby


class PostOffice(object):
    def __init__(self):
        self.main_connection = ConnectionPostOfficeEnd.MainConnection()
        self.connections = MasterConnection.MasterConnection()
        self.options = None
        self.results = Results.Results()
        self.training = Training.Training()
        self.standby = Standby.Standby()
        self.target_identification = TargetIdentification.TargetIdentification(self.connections, self.results, self.standby)
        self.message_counter = None
        self.waitConnections()

    def waitConnections(self):
        message = None
        while True:
            if message is not None:
                if message == c.START_MESSAGE:
                    message = self.start()
                    continue
                elif message == c.SETUP_MESSAGE:
                    setup_message = self.setup()
                    if setup_message == c.FAIL_MESSAGE:
                        self.connections.close()
                    print("Setup " + setup_message + "!")
                    self.main_connection.sendMessage(setup_message)
                elif message == c.STOP_MESSAGE:
                    print("Stop PostOffice")
                elif message == c.RESET_RESULTS_MESSAGE:
                    self.results.reset()
                elif message == c.SHOW_RESULTS_MESSAGE:
                    print(self.results)
                elif message == c.SAVE_RESULTS_MESSAGE:
                    self.main_connection.sendMessage(self.results.__repr__())
                elif message == c.LOAD_EEG_MESSAGE:
                    file_content = self.main_connection.receiveMessageBlock()
                    self.training.loadEeg(file_content)
                elif message == c.SAVE_EEG_MESSAGE:
                    self.main_connection.sendMessage(self.training.saveEeg())
                elif message == c.EXIT_MESSAGE:
                    self.exit()
                    return
                elif message in c.ROBOT_COMMANDS:
                    self.connections.sendRobotMessage(message)
                else:
                    print("Unknown message in PostOffice: " + str(message))
            message = self.main_connection.receiveMessagePoll(0.1)

    def getTotalTime(self, unlimited, test_time):
        return float("inf") if unlimited else test_time

    def getTarget(self, test_target, target_freqs, previous_target):
        if self.isRandom(test_target):
            targets = target_freqs.keys()
            if previous_target is not None and len(targets) > 1:
                targets.remove(previous_target)
            return random.choice(targets)
        elif test_target != c.TEST_NONE:
            return test_target
        else:
            return None

    def isRandom(self, test_target):
        return test_target == c.TEST_RANDOM

    def targetChangingLoop(self, options, target_freqs):
        total_time = self.getTotalTime(options[c.TEST_UNLIMITED], options[c.TEST_TIME])
        target = None
        while self.message_counter < total_time:
            target = self.getTarget(options[c.TEST_TARGET], target_freqs, target)
            if target is not None:
                self.training.collectExpectedTarget(target, self.message_counter)
                self.connections.sendTargetMessage(target)
            self.target_identification.resetTargetVariables()
            message = self.startPacketSending(target_freqs, target, total_time)
            if message is not None:
                return message
        self.main_connection.sendMessage(c.STOP_MESSAGE)
        return c.STOP_MESSAGE

    def setStandby(self, options):
        if options[c.DATA_TEST][c.TEST_STANDBY] == c.TEST_NONE:
            self.standby.disable()
        else:
            self.standby.enable()

    def setTraining(self, options):
        if options[c.DATA_TRAINING][c.TRAINING_RECORD] == c.TRAINING_RECORD_NORMAL:
            self.training.enableNormal()
        elif options[c.DATA_TRAINING][c.TRAINING_RECORD] == c.TRAINING_RECORD_NEUTRAL:
            self.training.enableNeutral()
        elif options[c.DATA_TRAINING][c.TRAINING_RECORD] == c.TRAINING_RECORD_DISABLED:
            self.training.disableRecording()
        else:
            raise Exception("Recording option menu in invalid state!")

    def setup(self):
        self.options = self.main_connection.receiveMessageBlock()
        self.connections.setup(self.options)
        self.setTraining(self.options)
        self.setStandby(self.options)
        self.setupStandby(self.options)
        if self.connections.setupSuccessful():
            self.results.setup(self.options[c.DATA_FREQS].values())
            self.training.setup()
            self.target_identification.setup(self.options[c.DATA_WEIGHTS], self.options[c.DATA_DIFFERENCES])
            return c.SUCCESS_MESSAGE
        else:
            return c.FAIL_MESSAGE

    def setupStandby(self, options):
        if self.standby.enabled:
            self.standby.setup(options[c.DATA_FREQS][options[c.DATA_TEST][c.TEST_STANDBY]])

    def exit(self):
        self.connections.close()
        self.main_connection.close()

    def start(self):
        self.message_counter = 0
        self.target_identification.resetResults(self.options[c.DATA_FREQS].values())
        self.connections.sendStartMessage()
        message = self.targetChangingLoop(
            self.options[c.DATA_TEST],
            self.options[c.DATA_FREQS],
        )
        self.results.trialEnded(self.message_counter)
        self.connections.sendStopMessage()
        return message

    def handleEmotivMessages(self, target_freqs, current_target):
        message = self.connections.receiveEmotivMessage()
        if message is not None:
            self.message_counter += 1
            self.training.collectPacket(message)
            self.connections.sendExtractionMessage(message)
            self.connections.sendPlotMessage(message)
            self.target_identification.handleFreqMessages(
                self.connections.receiveExtractionMessage(),
                target_freqs,
                current_target
            )

    def handleRobotMessages(self):
        message = self.connections.receiveRobotMessage()
        if message is not None:
            self.connections.sendTargetMessage(message)

    def startPacketSending(self, target_freqs, current_target, total_time):
        while not self.target_identification.need_new_target and self.message_counter < total_time:
            main_message = self.main_connection.receiveMessageInstant()
            if main_message in c.ROBOT_COMMANDS:
                self.connections.sendRobotMessage(main_message)
            elif main_message is not None:
                return main_message
            self.handleEmotivMessages(target_freqs, current_target)
            self.handleRobotMessages()
