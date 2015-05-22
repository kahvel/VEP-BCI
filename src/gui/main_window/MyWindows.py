__author__ = 'Anti'

import Tkinter


class TkWindow(Tkinter.Tk):
    def __init__(self, title, width, height, color="#eeeeee"):
        Tkinter.Tk.__init__(self)
        self.window_width = width
        self.window_height = height
        self.name = title
        self.title(title)
        self.resizable(0, 0)
        self.configure(background=color)

    def exit(self):
        self.destroy()
