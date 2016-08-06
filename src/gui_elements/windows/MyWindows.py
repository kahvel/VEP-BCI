import Tkinter


class TkWindow(Tkinter.Tk):
    def __init__(self, title):
        Tkinter.Tk.__init__(self)
        self.widget = self
        self.exitFlag = False
        self.name = title
        self.title(title)
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.exit)

    def exit(self):
        raise NotImplementedError("exit not implemented!")
