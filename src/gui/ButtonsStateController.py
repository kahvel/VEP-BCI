import constants as c


class ButtonsStateController(object):
    def __init__(self, main_frame, path_to_frame):
        self.path_to_frame = path_to_frame
        self.main_frame = main_frame

    def disableStart(self):
        self.main_frame.disableWidget(self.path_to_frame + (c.START_BUTTON,))

    def disableStop(self):
        self.main_frame.disableWidget(self.path_to_frame + (c.STOP_BUTTON,))

    def disableSetup(self):
        self.main_frame.disableWidget(self.path_to_frame + (c.SETUP_BUTTON,))

    def enableStart(self):
        self.main_frame.enableWidget(self.path_to_frame + (c.START_BUTTON,))

    def enableStop(self):
        self.main_frame.enableWidget(self.path_to_frame + (c.STOP_BUTTON,))

    def enableSetup(self):
        self.main_frame.enableWidget(self.path_to_frame + (c.SETUP_BUTTON,))

    def setInitialStates(self):
        self.disableStart()
        self.disableStop()
        self.enableSetup()

    def startClicked(self):
        self.disableSetup()
        self.disableStart()
        self.enableStop()

    def stopClicked(self):
        self.enableSetup()
        self.enableStart()
        self.disableStop()
