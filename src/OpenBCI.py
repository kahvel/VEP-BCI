import open_bci_v3
import threading

import constants as c


class OpenBCI(object):
    def __init__(self, connection):
        self.connection = connection
        self.boardThread = None
        self.board = None
        self.connection.waitMessages(self.start, self.cleanUp, lambda: None, self.connectionSetup)

    def closeDevice(self):
        if self.board is not None:
            self.board.disconnect()

    def cleanUp(self):
        self.closeDevice()
        self.connection.close()

    def connectionSetup(self):
        options = self.connection.receiveMessageBlock()
        daisy = True       # Use both boards
        port = None        # Automatically detect port
        log = True         # Logging
        aux = False        # Enable accelerometer/AUX data
        filtering = False  # Enable notch (50 Hz?) filter
        try:
            self.board = open_bci_v3.OpenBCIBoard(port=port, daisy=daisy, filter_data=filtering, scaled_output=True, log=log, aux=aux)
            print(self.board.getSampleRate(), self.board.getNbEEGChannels(), self.board.getNbAUXChannels())
            self.board.setImpedance(False)
            self.boardThread = threading.Thread(target=self.board.start_streaming, args=(self.callback, -1))
            self.boardThread.daemon = True  # will stop on exit
            return c.SETUP_SUCCEEDED_MESSAGE
        except OSError, e:
            print("OpenBCI setup failed:", e.message)
            return c.SETUP_FAILED_MESSAGE

    def callback(self, data):
        packet = {sensor: value for sensor, value in zip(c.SENSORS, data.channel_data)}
        print(packet["O1"], packet["O2"])
        self.connection.sendMessage(packet)

    def start(self):
        try:
            self.boardThread.start()
        except:
            raise
        while True:
            message = self.connection.receiveMessagePoll(0.1)
            if message is not None:
                self.closeDevice()
                return message
