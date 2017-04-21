import constants as c


class BufferClearer(object):
    def __init__(self, connections):
        self.clear_buffers = None
        self.source_option = None
        self.connections = connections
        self.previous_target = "FirstTarget"

    def setup(self, options):
        self.clear_buffers = options[c.DATA_CLEAR_BUFFERS]
        self.source_option = options[c.DATA_TEST][c.TEST_TAB_EEG_SOURCE_OPTION_MENU]

    def clearAfterDetection(self):
        if self.clear_buffers:# and self.source_option == c.EEG_SOURCE_DEVICE:
            self.connections.sendClearBuffersMessage()

    def clearAfterExpectedTargetChange(self, target):
        if target != self.previous_target and self.previous_target != "FirstTarget":
            if self.clear_buffers:  # and self.source_option != c.EEG_SOURCE_DEVICE:
                self.connections.sendClearBuffersMessage()
        self.previous_target = target
