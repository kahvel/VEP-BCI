__author__ = 'Anti'

from AbstractWindow import *
from Tkinter import Canvas

class TargetsWindow(Window):
    def __init__(self, background_textboxes, targets):
        super(TargetsWindow, self).__init__("Targets",
                                            int(background_textboxes["Width"].get()),
                                            int(background_textboxes["Height"].get()),
                                            color=background_textboxes["Color"].get())
        self.background_textboxes = background_textboxes
        self.targets = targets
        self.canvas = Canvas(self.window,
                             width=int(background_textboxes["Width"].get()),
                             height=int(background_textboxes["Height"].get()))
        self.canvas.place(x=0, y=0)

        for target in self.targets[1:]:
            rect = self.canvas.create_rectangle(int(target["x"]),
                                                int(target["y"]),
                                                int(target["x"])+int(target["Width"]),
                                                int(target["y"])+int(target["Height"]), fill=target["Color1"])

            # rect = Canvas(self.window, width=target.width, height=target.height, background="white")
            # rect.place(x=int(background_textboxes["Width"].get()), y=int(background_textboxes["Height"].get()))
            # r = rect.create_rectangle(0,0,target.width, target.height)
            self.flicker(target, rect)
        #self.focus()


    def flicker(self, target, rect, b=True):
        self.canvas.update()
        # rect.update()

        if b:
            self.canvas.itemconfig(rect, fill=target["Color2"])
            # rect.config(background=target.color2)
        else:
            self.canvas.itemconfig(rect, fill=target["Color1"])
            # rect.config(background=target.color1)
        self.canvas.after(int(1.0/int(target["Freq"])*1000), self.flicker, target, rect, not b)
        # rect.after(1/int(target.freq)*1000, self.flicker, target, rect, not b)