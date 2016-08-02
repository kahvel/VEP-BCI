from gui.widgets import Buttons
from gui.widgets.frames.notebooks import MainNotebook, TrainingNotebook
from gui.widgets.frames import Frame
import constants as c


class AbstractMainFrame(Frame.Frame):
    def __init__(self, parent, button_commands, row=0, column=0, **kwargs):
        Frame.Frame.__init__(self, parent, c.MAIN_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            self.getMainNotebook(button_commands),
            BottomFrame(self, button_commands, 1, 0)
        ))

    def getMainNotebook(self, button_commands):
        raise NotImplementedError("getMainNotebook not implemented!")


class BottomFrame(Frame.Frame):
    def __init__(self, parent, button_commands, row, column, **kwargs):
        start, stop, setup, save, load, exit = button_commands[c.BOTTOM_FRAME]
        Frame.Frame.__init__(self, parent, c.BOTTOM_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self, c.START_BUTTON, 0, 0, command=start),
            Buttons.Button(self, c.STOP_BUTTON,  0, 1, command=stop),
            Buttons.Button(self, c.SETUP_BUTTON, 0, 2, command=setup),
            Buttons.Button(self, c.SAVE_BUTTON,  0, 3, command=save),
            Buttons.Button(self, c.LOAD_BUTTON,  0, 4, command=load),
            Buttons.Button(self, c.EXIT_BUTTON,  0, 5, command=exit)
        ))


class MainFrame(AbstractMainFrame):
    def getMainNotebook(self, button_commands):
        return MainNotebook.MainNotebook(self, button_commands, 0, 0)


class TrainingMainFrame(AbstractMainFrame):
    def getMainNotebook(self, button_commands):
        return TrainingNotebook.TrainingNotebook(self, button_commands, 0, 0)
