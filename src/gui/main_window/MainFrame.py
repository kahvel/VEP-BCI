from gui_elements.widgets import Buttons
from gui.training_window import TrainingNotebook
from gui.main_window import MainNotebook
from gui_elements.widgets.frames import Frame
import constants as c


class AbstractMainFrame(Frame.Frame):
    def __init__(self, parent, row=0, column=0, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            self.getMainNotebook(),
            BottomFrame(self, 1, 0)
        ))

    def getMainNotebook(self):
        raise NotImplementedError("getMainNotebook not implemented!")


class BottomFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.BOTTOM_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self, c.START_BUTTON, 0, 0, command=self.startClicked),
            Buttons.Button(self, c.STOP_BUTTON,  0, 1, command=self.stopClicked),
            Buttons.Button(self, c.SETUP_BUTTON, 0, 2, command=self.setupClicked),
            Buttons.Button(self, c.SAVE_BUTTON,  0, 3, command=self.saveClicked),
            Buttons.Button(self, c.LOAD_BUTTON,  0, 4, command=self.loadClicked),
            Buttons.Button(self, c.EXIT_BUTTON,  0, 5, command=self.exitClicked)
        ))

    def startClicked(self):
        self.sendEventToRoot(lambda x: x.startBciEvent())

    def stopClicked(self):
        self.sendEventToRoot(lambda x: x.stopBciEvent())

    def setupClicked(self):
        self.sendEventToRoot(lambda x: x.setupBciEvent())

    def saveClicked(self):
        self.sendEventToRoot(lambda x: x.saveBciEvent(), True)

    def loadClicked(self):
        self.sendEventToRoot(lambda x: x.loadBciEvent(), True)

    def exitClicked(self):
        self.sendEventToRoot(lambda x: x.exitBciEvent())


class MainFrame(AbstractMainFrame):
    def getMainNotebook(self):
        return MainNotebook.MainNotebook(self, 0, 0)


class TrainingMainFrame(AbstractMainFrame):
    def getMainNotebook(self):
        return TrainingNotebook.TrainingNotebook(self, 0, 0)
