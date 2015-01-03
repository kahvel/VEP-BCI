__author__ = 'Anti'

import Tkinter


class FrameInterface(object):
    def __init__(self):
        self.frame_widgets = []

    def save(self, file):
        pass

    def load(self, values):
        pass

    def loadDefaultValues(self):
        pass

    def createFrame(self):
        pass


class Frame(Tkinter.Frame, FrameInterface):
    def __init__(self, parent):
        FrameInterface.__init__(self)
        Tkinter.Frame.__init__(self, parent)

    def getAllWidgets(self):
        return (widgets for widgets in self.frame_widgets)

    def createFrame(self):
        for frame_widgets in self.getAllWidgets():
            frame = Tkinter.Frame(self)
            for widget in frame_widgets:
                widget.create(frame)
            frame.pack()

    def save(self, file):
        pass
        # MyWindows.saveDict(self.textboxes, file)
        # MyWindows.saveDict(self.variables, file)

    def load(self, file):
        pass
        # MyWindows.updateDict(self.textboxes, file.readline().split(), MyWindows.updateTextbox)
        # MyWindows.updateDict(self.variables, file.readline().split(), MyWindows.updateVar)

    def loadDefaultValues(self):
        for frame in self.getAllWidgets():
            for widget in frame:
                widget.loadDefaultValue()
